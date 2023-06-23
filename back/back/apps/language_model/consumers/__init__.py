import json
from logging import getLogger

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

from back.apps.broker.consumers.message_types import RPCMessageType
from back.apps.broker.serializers.rpc import LLMRequestSerializer, RPCResponseSerializer
from back.apps.language_model.tasks import llm_query_task
from back.utils import WSStatusCodes

logger = getLogger(__name__)


class LLMConsumer(AsyncJsonWebsocketConsumer):
    """
    The consumer in responsible for
    """

    async def is_auth(self, scope):
        return (
            self.scope.get("user")
            and not isinstance(self.scope["user"], AnonymousUser)
            and await sync_to_async(
                self.scope["user"].groups.filter(name="RPC").exists
            )()
        )

    async def connect(self):
        if not await self.is_auth(self.scope):
            await self.close()
            return
        await self.accept()
        logger.debug(
            f"Starting new LLM WS connection (channel group: {self.channel_name})"
        )

    async def disconnect(self, close_code):
        logger.debug(f"Disconnecting from LLM consumer {close_code}")

    async def receive_json(self, content, **kwargs):
        serializer = RPCResponseSerializer(data=content)
        if not serializer.is_valid():
            await self.error_response(
                {"payload": {"errors": serializer.errors, "request_info": content}}
            )
            return

        if serializer.validated_data["type"] == RPCMessageType.llm_request.value:
            await self.llm_request_action(serializer.validated_data["data"])

    async def llm_request_action(self, data):
        serializer = LLMRequestSerializer(data=data)
        if not serializer.is_valid():
            await self.error_response({"payload": serializer.errors})
            return
        data = serializer.validated_data
        llm_query_task.delay(
            self.channel_name,
            data["model_id"],
            data["input_text"],
            data["bot_channel_name"],
        )

    async def send_llm_response(self, event):
        await self.send(
            json.dumps(
                {
                    "type": RPCMessageType.llm_request_result.value,
                    "status": WSStatusCodes.ok.value,
                    "payload": {**event["message"]},
                }
            )
        )

    async def error_response(self, data: dict):
        data["status"] = WSStatusCodes.bad_request.value
        data["type"] = RPCMessageType.error.value
        await self.send(json.dumps(data))
