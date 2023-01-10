import asyncio
import websockets
import json
from logging import getLogger

from riddler_sdk import settings

settings.configure()

logger = getLogger()


class RiddlerSDK:
    """
    This SDK helps on:
        - Defining the FSM handlers for transitions & states
        - Declare the FSM in Riddler
        - Translate inbound messages from Riddler into function calls (handlers) and vice-versa
    """
    def __init__(self, riddler_host: str, fsm_id: int = None):
        self.riddler_host = riddler_host
        self.fsm_id = fsm_id
        self.rpcs = {}
        self.uri = ""
        self.ws = None

    async def _connect(self):
        self.uri = f"{self.riddler_host}back/ws/broker/rpc/"
        if self.fsm_id is not None:
            self.uri = f"{self.riddler_host}back/ws/broker/rpc/{self.fsm_id}/"
        connection_error = True
        while connection_error:
            try:
                async with websockets.connect(self.uri) as ws:
                    self.ws = ws
                    logger.info(f"Connected to: {self.uri}")
                    await self.receive_loop()
            except (websockets.ConnectionClosed, ConnectionRefusedError):
                logger.info(f"Disconnected from {self.uri}, trying to reconnect in 1s")
                await asyncio.sleep(1)
            else:
                connection_error = False

    async def _disconnect(self):
        logger.info(f"Disconnecting from: {self.uri}")
        await self.ws.close()

    async def receive_loop(self):
        while True:
            logger.info("Waiting...")
            data = await self.ws.recv()
            data = json.loads(data)
            logger.info(f"Executing handler ::: {data['name']}")
            for handler in self.rpcs[data["name"]]:
                res = handler(data["ctx"])
                await self.ws.send(json.dumps(
                    {
                        "ctx": data["ctx"],
                        "payload": res,
                    }
                ))

    def connect(self):
        try:
            asyncio.run(self._connect())
        except KeyboardInterrupt:
            asyncio.run(self._disconnect())

    def rpc(self, name):
        """
        Decorator for registering functions as handlers
        Parameters
        ----------
        name : str
            Name to which the function will be called once we received it from riddler
        """
        def outer(func):
            def inner(ctx: dict):
                return func(ctx)

            if name not in self.rpcs:
                self.rpcs[name] = []
            self.rpcs[name].append(inner)

            return inner
        return outer
