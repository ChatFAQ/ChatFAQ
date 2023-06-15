import copy

import asyncio
import inspect
import json
import queue
import urllib.parse
from logging import getLogger
from typing import Callable, Union, Optional

import websockets
from chatfaq_sdk import settings
from chatfaq_sdk.conditions import Result
from chatfaq_sdk.fsm import FSMDefinition
from chatfaq_sdk.layers import Layer
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
        self.ws_rpc = None
        self.ws_llm = None
        self.queue_rpc = queue.Queue()
        self.queue_llm = queue.Queue()

        self.rpc_llm_request_futures = {}
        self.rpc_llm_request_msg_buffer = {}
        if self.fsm_def is not None:
            self.fsm_def.register_rpcs(self)

    def connect(self):
        try:
            asyncio.run(self.connexions())
        except KeyboardInterrupt:
            asyncio.run(self._disconnect())

    async def connexions(self):
        rpc_actions = {
            MessageType.rpc_request.value: self.rpc_request_callback,
            MessageType.error.value: self.error_callback,
        }
        llm_actions = {
            MessageType.llm_request_result.value: self.llm_request_result_callback,
            MessageType.error.value: self.error_callback,
        }

        await asyncio.gather(
            self.consumer("rpc", rpc_actions, on_connect=self.on_connect_rpc, is_rpc=True),
            self.consumer("llm", llm_actions, on_connect=None),
            self.producer(rpc_actions, is_rpc=True),
            self.producer(llm_actions),
        )

    async def _connect(self, consumer_route, actions, on_connect=None, is_rpc=False):
        self.uri = urllib.parse.urljoin(self.chatfaq_ws, f"back/ws/broker/{consumer_route}/")
        if is_rpc and self.fsm_name is not None and self.fsm_def is None:
            self.uri = f"{self.uri}{self.fsm_name}/"

        parsed_token = urllib.parse.quote(self.token)
        self.uri = f"{self.uri}?token={parsed_token}"
        connection_error = True
        while connection_error:
            try:
                logger.info(f"{'[RPC]' if is_rpc else '[LLM]'} Connecting to {self.uri}")
                async with websockets.connect(self.uri) as ws:
                    logger.info(f"{'[RPC]' if is_rpc else '[LLM]'} Connected")
                    if is_rpc:
                        self.ws_rpc = ws
                    else:
                        self.ws_llm = ws
                    if on_connect is not None:
                        await on_connect()
                    logger.info(f"{'[RPC]' if is_rpc else '[LLM]'} ---------------------- Listening...")
                    await self.receive_loop(actions, is_rpc)  # <----- "infinite" Connection Loop
            except (websockets.WebSocketException, ConnectionRefusedError):
                logger.info(f"{'[RPC]' if is_rpc else '[LLM]'} Connection error, retrying...")
                await asyncio.sleep(1)

    async def consumer(self, consumer_route, actions, on_connect=None, is_rpc=False):
        self.uri = urllib.parse.urljoin(self.chatfaq_ws, f"back/ws/broker/{consumer_route}/")
        if is_rpc and self.fsm_name is not None and self.fsm_def is None:
            self.uri = f"{self.uri}{self.fsm_name}/"

        parsed_token = urllib.parse.quote(self.token)
        self.uri = f"{self.uri}?token={parsed_token}"
        connection_error = True
        while connection_error:
            try:
                logger.info(f"{'[RPC]' if is_rpc else '[LLM]'} Connecting to {self.uri}")
                async with websockets.connect(self.uri) as ws:
                    logger.info(f"{'[RPC]' if is_rpc else '[LLM]'} Connected")
                    if is_rpc:
                        self.ws_rpc = ws
                    else:
                        self.ws_llm = ws
                    if on_connect is not None:
                        await on_connect()
                    logger.info(f"{'[RPC]' if is_rpc else '[LLM]'} ---------------------- Listening...")
                    await self._consume_loop(is_rpc)  # <----- "infinite" Connection Loop
            except (websockets.WebSocketException, ConnectionRefusedError):
                logger.info(f"{'[RPC]' if is_rpc else '[LLM]'} Connection error, retrying...")
                await asyncio.sleep(1)

    async def _consume_loop(self, is_rpc=False):
        while True:
            data = json.loads(await self.ws_rpc.recv()) if is_rpc else json.loads(await self.ws_llm.recv())
            if is_rpc:
                self.queue_rpc.put(data)
            else:
                self.queue_llm.put(data)

    async def producer(self, actions, is_rpc=False):
        while True:
            if not self.ws_rpc or not self.ws_llm or not self.ws_rpc.open or not self.ws_llm.open:
                await asyncio.sleep(0.01)
                continue
            try:
                data = self.queue_rpc.get(False) if is_rpc else self.queue_llm.get(False)
            except queue.Empty:
                await asyncio.sleep(0.01)
                continue

            if actions.get(data.get("type")) is not None:
                print(f"Action: {data.get('type')}")
                # await actions[data.get("type")](data["payload"])
                asyncio.create_task(actions[data.get("type")](data["payload"]))
            else:
                logger.error(f"Unknown action type: {data.get('type')}")

    async def receive_loop(self, actions, is_rpc):
        while True:
            data = json.loads(await self.ws_rpc.recv()) if is_rpc else json.loads(await self.ws_llm.recv())

            if actions.get(data.get("type")) is not None:
                await actions[data.get("type")](data["payload"])
            else:
                logger.error(f"Unknown action type: {data.get('type')}")

    async def on_connect_rpc(self):
        if self.fsm_def is not None:
            logger.info(f"Setting FSM by Definition {self.fsm_name}")
            await self.ws_rpc.send(
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
        await self.ws_rpc.close()
        await self.ws_llm.close()

    async def rpc_request_callback(self, payload):
        logger.info(f"[RPC] Executing ::: {payload['name']}")
        for handler in self.rpcs[payload["name"]]:
            async for res in self._run_handler(handler, payload["ctx"]):
                await self.ws_rpc.send(
                    json.dumps(
                        {
                            "type": MessageType.rpc_result.value,
                            "data": {
                                "ctx": payload["ctx"],
                                "payload": [res],
                            },
                        }
                    )
                )

    async def llm_request_result_callback(self, payload):
        if self.rpc_llm_request_msg_buffer.get(payload["bot_channel_name"]) is None:
            self.rpc_llm_request_msg_buffer[payload["bot_channel_name"]] = []

        self.rpc_llm_request_msg_buffer[payload["bot_channel_name"]].append(payload)
        self.rpc_llm_request_futures[payload["bot_channel_name"]].set_result(self.llm_result_streaming_generator(payload["bot_channel_name"]))

    def llm_result_streaming_generator(self, bot_channel_name):
        def _llm_result_streaming_generator():
            self.rpc_llm_request_futures[bot_channel_name] = asyncio.get_event_loop().create_future()
            _message_buffer = copy.deepcopy(self.rpc_llm_request_msg_buffer[bot_channel_name])
            self.rpc_llm_request_msg_buffer[bot_channel_name] = []

            if _message_buffer[-1]["final"]:
                return _message_buffer, False
            return _message_buffer, True
        return _llm_result_streaming_generator

    @staticmethod
    async def error_callback(payload):
        logger.error(f"Error from ChatFAQ's back-end server: {payload}")

    async def send_llm_request(self, model_id, input_text, bot_channel_name):
        logger.info(f"[LLM] Requesting LLM (model {model_id})")
        self.rpc_llm_request_futures[bot_channel_name] = asyncio.get_event_loop().create_future()
        await self.ws_llm.send(
            json.dumps({
                "type": MessageType.llm_request.value,
                "data": {
                    "model_id": model_id,
                    "input_text": input_text,
                    "bot_channel_name": bot_channel_name,
                },
            })
        )

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

    async def _run_handler(self, handler, data):
        layers = handler(data)
        if inspect.isgenerator(layers):
            for layer in layers:
                async for _repr in self._layer_to_dict(layer, data):
                    yield _repr
        else:
            async for _repr in self._layer_to_dict(layers, data):
                yield _repr

    async def _layer_to_dict(self, layer, data):
        if False and not isinstance(layer, Layer) and not isinstance(layer, Result):
            raise Exception(
                "RPCs results should return either Layers type objects or result type objects"
            )
        _repr = layer.dict_repr(self, data)
        # check if is generator
        async for r in _repr:
            yield r
