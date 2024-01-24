import json
from logging import getLogger

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

from back.apps.broker.consumers.message_types import ParseMessageType
from back.apps.broker.models import RemoteSDKParsers
from back.apps.broker.serializers.rpc import ParseResponseSerializer, RegisterParsersSerializer
from back.apps.language_model.serializers.data import KnowledgeItemSerializer
from back.utils import WSStatusCodes

logger = getLogger(__name__)


class ParseConsumer(AsyncJsonWebsocketConsumer):
    """
    The consumer in responsible for
    """

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
        await self.accept()
        logger.debug(
            f"Starting new Parse WS connection (channel group: {self.channel_name})"
        )

    async def disconnect(self, close_code):
        logger.debug(f"Disconnecting from Parse consumer {close_code}")
        await database_sync_to_async(RemoteSDKParsers.remove)(self.channel_name)  # Remove from round robin queue

    async def receive_json(self, content, **kwargs):
        serializer = ParseResponseSerializer(data=content)
        if not serializer.is_valid():
            await self.error_response(
                {"payload": {"errors": serializer.errors, "request_info": content}}
            )
            return

        if serializer.validated_data["type"] == ParseMessageType.register_parsers.value:
            await self.register_parsers(serializer.validated_data["data"])
        elif serializer.validated_data["type"] == ParseMessageType.parser_result_ki.value:
            await self.save_ki_from_parser(serializer.validated_data["data"])

    async def register_parsers(self, data):
        serializer = RegisterParsersSerializer(data=data)
        if not serializer.is_valid():
            await self.error_response({"payload": serializer.errors})
            return
        data = serializer.validated_data
        for parser in data["parsers"]:
            await database_sync_to_async(RemoteSDKParsers.add)(
                self.channel_name, parser
            )

    async def save_ki_from_parser(self, data):
        serializer = KnowledgeItemSerializer(data=data)
        if not await database_sync_to_async(serializer.is_valid)():
            await self.error_response({"payload": serializer.errors})
            return
        await database_sync_to_async(serializer.save)()

    async def error_response(self, data: dict):
        data["status"] = WSStatusCodes.bad_request.value
        data["type"] = ParseMessageType.error.value
        await self.send(json.dumps(data))

    async def send_data_source_to_parse(self, event):
        await self.send(
            json.dumps(
                {
                    "type": event["parser"],
                    "status": WSStatusCodes.ok.value,
                    "payload": {**event["payload"]},
                }
            )
        )
