from channels.generic.websocket import AsyncJsonWebsocketConsumer


class PassiveAggressiveConsumer(AsyncJsonWebsocketConsumer):
    """
    That's a websocket that will accept then close all connections. It is a
    demo of how you can do websockets, but it does not provide any feature.
    """

    async def connect(self):
        await self.accept()
        await self.close(3000)
