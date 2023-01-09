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

    async def _connect(self):
        uri = f"{self.riddler_host}back/ws/broker/rpc/"
        if self.fsm_id is not None:
            uri = f"{self.riddler_host}back/ws/broker/rpc/{self.fsm_id}/"
        async with websockets.connect(uri) as websocket:
            logger.info(f"Connected to: {uri}")
            while True:
                logger.info("Waiting...")
                data = await websocket.recv()
                data = json.loads(data)
                logger.info(f"Executing handler ::: {data['name']}")
                for handler in self.rpcs[data["name"]]:
                    res = handler(data["ctx"])
                    await websocket.send(json.dumps(
                        {
                            "ctx": data["ctx"],
                            "payload": res,
                        }
                    ))

    def connect(self):
        asyncio.run(self._connect())

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
