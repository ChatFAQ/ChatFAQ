import asyncio
import inspect
import json
from logging import getLogger
from typing import Callable, Union

import websockets
from riddler_sdk import settings
from riddler_sdk.conditions import Result
from riddler_sdk.fsm import FSMDefinition
from riddler_sdk.layers import Layer
from riddler_sdk.ws.messages import MessageType

settings.configure()

logger = getLogger()


class RiddlerSDK:
    """
    This SDK helps on:
        - Defining the FSM handlers for transitions & states
        - Declare the FSM in Riddler
        - Translate inbound messages from Riddler into function calls (handlers) and vice-versa
    """

    def __init__(
        self,
        riddler_host: str,
        fsm_name: Union[int, str, None],
        fsm_def: Union[FSMDefinition, None] = None,
    ):
        """
        Parameters
        ----------
        riddler_host: str
            The WS address of your Riddler server
        fsm_name: Union[int, str, None]
            The id or name of the FSM you are going to associate this client to. If you are going to create a new FSM
            then it should be the name you are going to give to the new created FSM

        fsm_def: Union[FSMDefinition, None]
            The FSM you are going to create in the Riddler server, if already exists a FSM definition on the server with
            the same struincurre then that one will be reused and your 'name' parameter will be ignored
        """
        if fsm_def is dict and fsm_name is None:
            raise Exception("If you declare a FSM definition you should provide a name")
        self.riddler_host = riddler_host
        self.fsm_name = fsm_name
        self.fsm_def = fsm_def
        self.rpcs = {}
        # _rpcs is just an auxiliary variable to register the rpcs without the decorator function just so we know if we
        # already registered that rpc under that name and avoid duplicates
        self._rpcs = {}
        self.uri = ""
        self.ws = None
        if self.fsm_def is not None:
            self.fsm_def.register_rpcs(self)

    async def _connect(self):
        self.uri = f"{self.riddler_host}back/ws/broker/rpc/"
        if self.fsm_name is not None and self.fsm_def is None:
            self.uri = f"{self.riddler_host}back/ws/broker/rpc/{self.fsm_name}/"

        connection_error = True
        while connection_error:
            try:
                logger.info(f"Connecting to: {self.uri}")
                async with websockets.connect(self.uri) as ws:
                    logger.info(f"Connected")
                    self.ws = ws
                    await self.on_connect()
                    await self.receive_loop()
            except (websockets.WebSocketException, ConnectionRefusedError):
                logger.info(f"Disconnected from {self.uri}, trying to reconnect in 1s")
                await asyncio.sleep(1)
            else:
                connection_error = False

    def connect(self):
        try:
            asyncio.run(self._connect())
        except KeyboardInterrupt:
            asyncio.run(self._disconnect())

    async def on_connect(self):
        if self.fsm_def is not None:
            logger.info(f"Setting FSM by Definition {self.fsm_name}")
            await self.ws.send(
                json.dumps(
                    {
                        "type": MessageType.fsm_def.value,
                        "data": {
                            "name": self.fsm_name,
                            "definition": self.fsm_def.to_json(),
                        },
                    }
                )
            )

    async def _disconnect(self):
        logger.info(f"Disconnecting from: {self.uri}")
        await self.ws.close()

    async def receive_loop(self):
        logger.info(" ---------------------- Listening...")
        while True:
            data = await self.ws.recv()
            data = json.loads(data)
            if data.get("type") == MessageType.rpc_request.value:
                data = data["payload"]
                logger.info(f"Executing RPC ::: {data['name']}")
                for handler in self.rpcs[data["name"]]:
                    res = self._run_handler(handler, data["ctx"])
                    await self.ws.send(
                        json.dumps(
                            {
                                "type": MessageType.rpc_result.value,
                                "data": {
                                    "ctx": data["ctx"],
                                    "payload": res,
                                },
                            }
                        )
                    )
            elif data.get("type") == MessageType.error.value:
                data = data["payload"]
                logger.error(f"Error from Riddler server: {data}")

    def rpc(self, name: str) -> Callable:
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
                self._rpcs[name] = []
                self.rpcs[name] = []
            if func not in self._rpcs[name]:
                self._rpcs[name].append(func)
                self.rpcs[name].append(inner)

            return inner

        return outer

    @classmethod
    def _run_handler(cls, handler, data):
        res = handler(data)
        if inspect.isgenerator(res):
            return [cls._layer_to_json(item) for item in res]
        return cls._layer_to_json(res)

    @staticmethod
    def _layer_to_json(rpc_result):
        if not isinstance(rpc_result, Layer) and not isinstance(rpc_result, Result):
            raise Exception(
                "RPCs results should return either Layers type objects or result type objects"
            )
        return rpc_result.to_json()
