import json
from logging import getLogger

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

from back.apps.broker.consumers.message_types import ParseMessageType
from back.apps.broker.models import RemoteSDKParsers
from back.apps.broker.serializers.rpc import ParseResponseSerializer, RegisterParsersSerializer, ParsersFinishSerializer
from back.apps.language_model.models.tasks import RayTaskState
from back.apps.language_model.serializers.data import KnowledgeItemSerializer
from back.utils import WSStatusCodes

logger = getLogger(__name__)


class ParseConsumer(AsyncJsonWebsocketConsumer):
    """
    The consumer in responsible for
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parse_tasks = []

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

        # Fail pending tasks:
        for task_id in self.parse_tasks:
            task = await database_sync_to_async(RayTaskState.objects.filter(task_id=task_id).first)()
            if task is None:
                continue
            if task.state != RayTaskState.STATE_CHOICES_DICT["FINISHED"]:
                task.state = RayTaskState.STATE_CHOICES_DICT["FAILED"]
                await database_sync_to_async(task.save)()

        # Remove from round robin queue
        await database_sync_to_async(RemoteSDKParsers.remove)(self.channel_name)

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
        elif serializer.validated_data["type"] == ParseMessageType.parser_finished.value:
            await self.parser_finished(serializer.validated_data["data"])

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

    async def parser_finished(self, data):
        serializer = ParsersFinishSerializer(data=data)
        if not await database_sync_to_async(serializer.is_valid)():
            await self.error_response({"payload": serializer.errors})
            return
        task = await database_sync_to_async(RayTaskState.objects.filter(task_id=serializer.validated_data["task_id"]).first)()
        if task is None:
            await self.error_response({"payload": {"errors": "Task not found"}})
            return
        task.state = RayTaskState.STATE_CHOICES_DICT["FINISHED"]
        await database_sync_to_async(task.save)()

    async def error_response(self, data: dict):
        data["status"] = WSStatusCodes.bad_request.value
        data["type"] = ParseMessageType.error.value
        await self.send(json.dumps(data))

    async def send_data_source_to_parse(self, event):
        if event["payload"].get("task_id") is not None:
            self.parse_tasks.append(event["payload"]["task_id"])

        await self.send(
            json.dumps(
                {
                    "type": event["parser"],
                    "status": WSStatusCodes.ok.value,
                    "payload": {**event["payload"]},
                }
            )
        )
