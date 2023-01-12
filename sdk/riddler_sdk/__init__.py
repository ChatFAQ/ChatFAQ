import inspect
import asyncio
import websockets
import json
from logging import getLogger

from riddler_sdk import settings
from riddler_sdk.layers import Layer

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

    def connect(self):
        try:
            asyncio.run(self._connect())
        except KeyboardInterrupt:
            asyncio.run(self._disconnect())

    async def _disconnect(self):
        logger.info(f"Disconnecting from: {self.uri}")
        await self.ws.close()

    async def receive_loop(self):
        logger.info("Listening...")
        while True:
            data = await self.ws.recv()
            data = json.loads(data)
            logger.info(f"Executing RPC ::: {data['name']}")
            for handler in self.rpcs[data["name"]]:
                res = self._run_handler(handler, data["ctx"])
                await self.ws.send(json.dumps(
                    {
                        "ctx": data["ctx"],
                        "payload": res,
                    }
                ))

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

    @classmethod
    def _run_handler(cls, handler, data):
        res = handler(data)
        if inspect.isgenerator(res):
            return [cls._layer_to_json(item) for item in res]
        return res

    @staticmethod
    def _layer_to_json(layer):
        if not isinstance(layer, Layer):
            raise Exception("RPCs of actions should only return layers")
        return layer.to_json()
