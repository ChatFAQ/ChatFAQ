import uuid

import json
from logging import getLogger

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

from back.apps.broker.consumers.message_types import RPCMessageType
from back.apps.broker.serializers.rpc import (
    RPCFSMDefSerializer,
    RPCResponseSerializer,
    RPCResultSerializer,
)
from back.apps.fsm.models import FSMDefinition
from back.apps.broker.models import ConsumerRoundRobinQueue
from back.apps.fsm.serializers import FSMSerializer
from back.common.abs.bot_consumers.ws import WSBotConsumer
from back.utils import WSStatusCodes

logger = getLogger(__name__)


class RPCConsumer(AsyncJsonWebsocketConsumer):
    """
    The consumer in responsible for keeping the connection of the Remote Procedure Calls servers and associate it to a
    FSM definition. Any state/transition declared on the FSM unknown to the system will be considered a RCP and piped it
     to the corresponding connection.
    """

    serializer_class = FSMSerializer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fsm_id = None
        self.uuid = str(uuid.uuid4())

    def get_group_name(self):
        return f"rpc_{self.fsm_id}_{self.uuid}"

    async def is_auth(self, scope):
        return (
            self.scope.get("user")
            and not isinstance(self.scope["user"], AnonymousUser)
            and await database_sync_to_async(
                self.scope["user"].groups.filter(name="RPC").exists
            )()
        )

    async def connect(self):
        if not await self.is_auth(self.scope):
            await self.close()
            return

        fsm_id_or_name = self.scope["url_route"]["kwargs"].get("fsm_id")
        fsm = await database_sync_to_async(FSMDefinition.get_by_id_or_name)(fsm_id_or_name)
        if fsm is None:
            logger.debug(
                "New RPC WS Connection without fsm_id, the fsm definition will have to be declared later on "
                "with a 'fsm_def' message type"
            )
        else:
            logger.info(
                f"Setting existing FSM Definition ({fsm.name} ({fsm.pk})) by ID/name"
            )
            self.fsm_id = fsm.pk
            await self.channel_layer.group_add(self.get_group_name(), self.channel_name, rr_group_key=fsm.pk)
        await self.accept()
        if fsm is None and fsm_id_or_name is not None:
            await self.error_response(
                {
                    "payload": {
                        "errors": f"It does not exists an FSM with the next id/name: {fsm_id_or_name}"
                    }
                }
            )
        logger.debug(
            f"Starting new RPC WS connection (channel group: {self.get_group_name()})"
        )

    async def disconnect(self, close_code):
        logger.debug(f"Disconnecting from RPC consumer")
        # Leave room group
        await self.channel_layer.group_discard(self.get_group_name(), self.channel_name)
        await database_sync_to_async(ConsumerRoundRobinQueue.remove)(self.get_group_name())  # Remove from round robin queue

    async def receive_json(self, content, **kwargs):
        serializer = RPCResponseSerializer(data=content)
        if not serializer.is_valid():
            await self.error_response(
                {"payload": {"errors": serializer.errors, "request_info": content}}
            )
            return

        if serializer.validated_data["type"] == RPCMessageType.fsm_def.value:
            await self.manage_fsm_def(serializer.validated_data["data"])
        elif serializer.validated_data["type"] == RPCMessageType.rpc_result.value:
            await self.manage_rpc_result(serializer.validated_data["data"])

    async def manage_fsm_def(self, data):
        serializer = RPCFSMDefSerializer(data=data)
        serializer.is_valid()
        if not serializer.is_valid():
            await self.error_response(
                {"payload": {"errors": serializer.errors, "request_info": data}}
            )
            return
        data = serializer.validated_data
        if self.fsm_id is not None:
            await self.channel_layer.group_discard(
                self.get_group_name(), self.channel_name
            )
        fsm, created, errors = await database_sync_to_async(
            FSMDefinition.get_or_create_from_definition
        )(data["name"], data["definition"])
        if errors:
            await self.error_response(
                {"payload": {"errors": errors, "request_info": data}}
            )
            return
        self.fsm_id = fsm.pk

        if created:
            logger.info(
                f"Created new FSM Definition from the RPC server: {data['name']}"
            )
        else:
            logger.info(
                f"Setting existing FSM Definition ({fsm.name} ({fsm.pk})) by provided definition"
            )
        await self.channel_layer.group_add(self.get_group_name(), self.channel_name)
        await database_sync_to_async(ConsumerRoundRobinQueue.add)(
            self.get_group_name(), self.fsm_id
        )  # Add to round robin queue

    async def manage_rpc_result(self, data):
        serializer = RPCResultSerializer(data=data)
        serializer.is_valid()
        if not serializer.is_valid():
            await self.error_response({"payload": serializer.errors})
            return
        data = serializer.validated_data
        ctx = data["ctx"]
        del data["ctx"]
        res = {
            "type": "rpc_response",
            "status": WSStatusCodes.ok.value,
            **data,
        }
        conversation_id = ctx["conversation_id"]
        await self.channel_layer.group_send(
            WSBotConsumer.create_group_name(conversation_id), res
        )

    async def rpc_call(self, data: dict):
        data["status"] = WSStatusCodes.ok.value
        data["type"] = RPCMessageType.rpc_request.value
        await self.send(json.dumps(data))

    async def error_response(self, data: dict):
        data["status"] = WSStatusCodes.bad_request.value
        data["type"] = RPCMessageType.error.value
        await self.send(json.dumps(data))
