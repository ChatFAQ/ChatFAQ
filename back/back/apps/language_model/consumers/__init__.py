import json
from logging import getLogger

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

from back.apps.broker.consumers.message_types import RPCMessageType
from back.apps.broker.serializers.rpc import (
    RPCResponseSerializer, LLMRequestSerializer,
)
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
            await self.manage_llm_request(serializer.validated_data["data"])

    async def manage_llm_request(self, data):
        serializer = LLMRequestSerializer(data=data)
        if not serializer.is_valid():
            await self.error_response({"payload": serializer.errors})
            return
        data = serializer.validated_data
        res = {
            "type": RPCMessageType.llm_request_result.value,
            "status": WSStatusCodes.ok.value,
            "payload": {
                "status": "finished",
                "res": f"LLM ({data['model_id']}) generated text from {data['input_text']}",
                "context": [{"url": "https://www.google.com"}, {"url": "https://www.shopify.com"}]
            },
        }
        print(111)
        await self.send(json.dumps(res))
        print(222)

    async def error_response(self, data: dict):
        data["status"] = WSStatusCodes.bad_request.value
        data["type"] = RPCMessageType.error.value
        await self.send(json.dumps(data))
