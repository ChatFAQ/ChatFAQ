import asyncio
from logging import getLogger

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

from ray.util.state import api as ray_api

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
        self.loop_task = asyncio.create_task(self.send_tasks())

    async def disconnect(self, close_code):
        logger.debug(f"Disconnecting from Progress Tasks consumer {close_code}")
        await self.channel_layer.group_discard("tasks", self.channel_name)

        if hasattr(self, 'loop_task') and not self.loop_task.done():
            self.loop_task.cancel()
            try:
                await self.loop_task
            except asyncio.CancelledError:
                print("Task was cancelled")
            except Exception as e:
                print(f"Unexpected error: {e}")

        await super().disconnect(close_code)

    async def send_tasks(self):
        while True:
            await asyncio.sleep(1)
            await self.send_json([j.__dict__ for j in ray_api.list_tasks()])
