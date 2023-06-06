import asyncio
import inspect
import json
import urllib.parse
from logging import getLogger
from typing import Callable, Union, Optional

import websockets
from chatfaq_sdk import settings
from chatfaq_sdk.conditions import Result
from chatfaq_sdk.fsm import FSMDefinition
from chatfaq_sdk.layers import Layer #  , LMGeneratedText
from chatfaq_sdk.api.messages import MessageType

settings.configure()

logger = getLogger()


class ChatFAQSDK:
    """
    This SDK helps on:
        - Defining the FSM handlers for transitions & states
        - Declare the FSM in ChatFAQ's back-end server
        - Translate inbound messages from ChatFAQ's back-end server into function calls (handlers) and vice-versa
    """

    def __init__(
        self,
        chatfaq_retrieval_http: str,
        chatfaq_ws: str,
        token: str,
        fsm_name: Optional[Union[int, str]],
        fsm_definition: Optional[FSMDefinition] = None
    ):
        """
        Parameters
        ----------
        chatfaq_retrieval_http: str
            The HTTP address of your ChatFAQ's back-end server

        chatfaq_ws: str
            The WS address of your ChatFAQ's back-end server

        token: str
            The auth token of your ChatFAQ's back-end server

        fsm_name: Union[int, str, None]
            The id or name of the FSM you are going to associate this client to. If you are going to create a new FSM
            then it should be the name you are going to give to the new created FSM

        fsm_definition: Union[FSMDefinition, None]
            The FSM you are going to create in the ChatFAQ's back-end server, if already exists a FSM definition on the server with
            the same struincurre then that one will be reused and your 'name' parameter will be ignored
        """
        if fsm_definition is dict and fsm_name is None:
            raise Exception("If you declare a FSM definition you should provide a name")
        self.chatfaq_retrieval_http = chatfaq_retrieval_http
        self.chatfaq_ws = chatfaq_ws
        self.token = token
        self.fsm_name = fsm_name
        self.fsm_def = fsm_definition
        self.rpcs = {}
        # _rpcs is just an auxiliary variable to register the rpcs without the decorator function just so we know if we
        # already registered that rpc under that name and avoid duplicates
        self._rpcs = {}
        self.uri = ""
        self.ws = None
        if self.fsm_def is not None:
            self.fsm_def.register_rpcs(self)

        # for model_id in fsm_definition.pre_load_models:
        #     LMGeneratedText.get_model(model_id, self)

    async def _connect(self):
        self.uri = urllib.parse.urljoin(self.chatfaq_ws, "back/ws/broker/rpc/")
        if self.fsm_name is not None and self.fsm_def is None:
            self.uri = urllib.parse.urljoin(self.chatfaq_ws, f"back/ws/broker/rpc/{self.fsm_name}/")
        parsed_token = urllib.parse.quote(self.token)
        self.uri = f"{self.uri}?token={parsed_token}"
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
                            "definition": self.fsm_def.to_dict_repr(),
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
                logger.error(f"Error from ChatFAQ's back-end server: {data}")

    def rpc(self, name: str) -> Callable:
        """
        Decorator for registering functions as handlers
        Parameters
        ----------
        name : str
            Name to which the function will be called once we received it from ChatFAQ's back-end server
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

    def _run_handler(self, handler, data):
        res = handler(data)
        if inspect.isgenerator(res):
            return [self._layer_to_dict(item) for item in res]
        return self._layer_to_dict(res)

    def _layer_to_dict(self, rpc_result):
        if not isinstance(rpc_result, Layer) and not isinstance(rpc_result, Result):
            raise Exception(
                "RPCs results should return either Layers type objects or result type objects"
            )
        return rpc_result.dict_repr(self)
