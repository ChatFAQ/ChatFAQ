import json
from logging import getLogger

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

from back.utils.ray_connection import ray_and_celery_tasks

logger = getLogger(__name__)


class TasksProgressConsumer(AsyncJsonWebsocketConsumer):
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
            logger.debug(
                f"TasksProgressConsumer - no auth"
            )
            return
        logger.debug(
            f"TasksProgressConsumer - auth: {self.scope.get('user')}"
        )
        await self.channel_layer.group_add("tasks", self.channel_name)
        await self.accept()
        await self.send_data(None)

    async def disconnect(self, close_code):
        logger.debug(f"Disconnecting from Progress Tasks consumer {close_code}")
        await self.channel_layer.group_discard("tasks", self.channel_name)

    async def send_data(self, event):
        @database_sync_to_async
        def get_all_tasks():
            return ray_and_celery_tasks(current=True)
        tasks = await get_all_tasks()
        await self.send(json.dumps(tasks))
