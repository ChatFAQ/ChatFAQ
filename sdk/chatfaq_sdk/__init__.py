import asyncio
import copy
import inspect
import json
import queue
import urllib.parse
import uuid
from functools import wraps
from logging import getLogger
from typing import Callable, Optional, Union

import httpx
import websockets

from chatfaq_sdk import settings
from chatfaq_sdk.conditions import Condition
from chatfaq_sdk.data_source_parsers import DataSourceParser
from chatfaq_sdk.fsm import FSMDefinition
from chatfaq_sdk.layers import Layer
from chatfaq_sdk.types import DataSource, WSType
from chatfaq_sdk.types.messages import MessageType, RPCNodeType

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
        chatfaq_ws: str,
        chatfaq_http: str,
        token: str,
        fsm_name: Optional[Union[int, str]],
        fsm_definition: Optional[FSMDefinition] = None,
        data_source_parsers: Optional[dict[str, DataSourceParser]] = None,
    ):
        """
        Parameters
        ----------
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
        self.chatfaq_ws = chatfaq_ws
        self.chatfaq_http = chatfaq_http
        self.token = token
        self.fsm_name = fsm_name
        self.fsm_def = fsm_definition
        self.data_source_parsers = data_source_parsers
        self.rpcs = {}
        # _rpcs is just an auxiliary variable to register the rpcs without the decorator function just so we know if we
        # already registered that rpc under that name and avoid duplicates
        self._rpcs = {}

        self.llm_request_futures = {}
        self.llm_request_msg_buffer = {}
        if self.fsm_def is not None:
            self.fsm_def.register_rpcs(self)

    def connect(self):
        try:
            asyncio.run(self.connexions())
        except KeyboardInterrupt:
            asyncio.run(self._disconnect())

    async def connexions(self):
        setattr(self, f"ws_{WSType.rpc.value}", None)
        setattr(self, f"ws_{WSType.ai.value}", None)
        rpc_actions = {
            MessageType.rpc_request.value: self.rpc_request_callback,
            MessageType.error.value: self.error_callback,
        }
        ai_actions = {
            MessageType.llm_request_result.value: self.llm_request_result_callback,
            MessageType.rag_request_result.value: self.llm_request_result_callback,
            MessageType.error.value: self.error_callback,
        }
        coros_or_futures = [
            self.consumer(WSType.rpc.value, on_connect=self.on_connect_rpc),
            self.consumer(WSType.ai.value, on_connect=None),
            self.producer(rpc_actions, WSType.rpc.value),
            self.producer(ai_actions, WSType.ai.value),
        ]
        if self.data_source_parsers:
            setattr(self, f"ws_{WSType.parse.value}", None)
            parser_actions = {
                key: self.parsing_wrapper(value)
                for key, value in self.data_source_parsers.items()
            }
            parser_actions[MessageType.error.value] = self.error_callback
            coros_or_futures += [
                self.consumer(WSType.parse.value, on_connect=self.on_connect_parsing),
                self.producer(parser_actions, WSType.parse.value),
            ]

        await asyncio.gather(
            *coros_or_futures,
        )

    async def consumer(self, consumer_route, on_connect=None):
        setattr(self, f"queue_{consumer_route}", queue.Queue())
        uri = urllib.parse.urljoin(self.chatfaq_ws, f"back/ws/broker/{consumer_route}/")
        if (
            consumer_route == WSType.rpc.value
            and self.fsm_name is not None
            and self.fsm_def is None
        ):
            uri = f"{uri}{self.fsm_name}/"

        parsed_token = urllib.parse.quote(self.token)
        uri = f"{uri}?token={parsed_token}"
        while True:
            try:
                logger.info(f"[{consumer_route.upper()}] Connecting to {uri}")
                async with websockets.connect(uri) as ws:
                    logger.info(f"[{consumer_route.upper()}] Connected")
                    setattr(self, f"ws_{consumer_route}", ws)
                    if on_connect is not None:
                        await on_connect()
                    logger.info(
                        f"[{consumer_route.upper()}] ---------------------- Listening..."
                    )
                    await self._consume_loop(
                        consumer_route
                    )  # <----- "infinite" Connection Loop
            except (websockets.WebSocketException, ConnectionRefusedError):
                logger.info(f"{consumer_route.upper()} Connection error, retrying...")
                await asyncio.sleep(1)

    async def _consume_loop(self, consumer_route):
        while True:
            data = json.loads(await getattr(self, f"ws_{consumer_route}").recv())
            getattr(self, f"queue_{consumer_route}").put(data)

    async def producer(self, actions, consumer_route):
        ws_attrs = [attr for attr in dir(self) if attr.startswith("ws_")]
        while True:
            if any(
                getattr(self, ws_attr) is None or not getattr(self, ws_attr).open
                for ws_attr in ws_attrs
            ):
                await asyncio.sleep(0.01)
                continue
            try:
                data = getattr(self, f"queue_{consumer_route}").get(False)
            except queue.Empty:
                await asyncio.sleep(0.01)
                continue

            if actions.get(data.get("type")) is not None:
                asyncio.create_task(actions[data.get("type")](data["payload"]))
            else:
                logger.error(f"Unknown action type: {data.get('type')}")

    async def on_connect_rpc(self):
        if self.fsm_def is not None:
            logger.info(f"[RPC] Setting FSM by definition {self.fsm_name}")
            await getattr(self, f"ws_{WSType.rpc.value}").send(
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

    async def on_connect_parsing(self):
        if self.data_source_parsers is not None:
            parsers = list(self.data_source_parsers.keys())
            logger.info(f"[PARSE] Registering Data Source Parsers {parsers}")
            await getattr(self, f"ws_{WSType.parse.value}").send(
                json.dumps(
                    {
                        "type": MessageType.register_parsers.value,
                        "data": {
                            "parsers": parsers,
                        },
                    }
                )
            )

    async def _disconnect(self):
        logger.info("Shutting Down...")
        wss = [getattr(self, attr) for attr in dir(self) if attr.startswith("ws_")]
        for ws in wss:
            if ws is not None and ws.open:
                await ws.close()

    async def rpc_request_callback(self, payload):
        logger.info(f"[RPC] Executing ::: {payload['name']}")
        for handler_index, handler in enumerate(self.rpcs[payload["name"]]):
            stack_id = str(uuid.uuid4())
            logger.info(f"[RPC]     |---> ::: {handler}")

            async for res, last_from_handler, node_type in self._run_handler(
                handler, payload["ctx"]
            ):
                await getattr(self, f"ws_{WSType.rpc.value}").send(
                    json.dumps(
                        {
                            "type": MessageType.rpc_result.value,
                            "data": {
                                "ctx": payload["ctx"],
                                "node_type": node_type,
                                "stack_id": stack_id,
                                "stack": res,
                                "last": handler_index
                                == len(self.rpcs[payload["name"]]) - 1
                                and last_from_handler,
                            },
                        }
                    )
                )

    async def llm_request_result_callback(self, payload):
        # mesages could come at a faster rate than the handler can process them, so we need to buffer them
        if self.llm_request_msg_buffer.get(payload["bot_channel_name"]) is None:
            self.llm_request_msg_buffer[payload["bot_channel_name"]] = []
        self.llm_request_msg_buffer[payload["bot_channel_name"]].append(payload)

        # then we set future result to the generator as an indicator to the handler that it can start processing the
        # messages. The generator will be consumed by the handler once awaited, and it will take care of resetting the
        # buffer and setting the future again, in the meanwhile messages can still arrive and we keep buffering
        if not self.llm_request_futures[payload["bot_channel_name"]].done():
            self.llm_request_futures[payload["bot_channel_name"]].set_result(
                self.llm_result_streaming_generator(payload["bot_channel_name"])
            )

    def llm_result_streaming_generator(self, bot_channel_name):
        # The generator will be consumed by the handler once awaited, and it will take care of resetting the buffer and
        # setting the future again
        def _llm_result_streaming_generator():
            self.llm_request_futures[bot_channel_name] = (
                asyncio.get_event_loop().create_future()
            )

            _message_buffer = copy.deepcopy(
                self.llm_request_msg_buffer[bot_channel_name]
            )

            self.llm_request_msg_buffer[bot_channel_name] = []

            return _message_buffer

        return _llm_result_streaming_generator

    @staticmethod
    async def error_callback(payload):
        logger.error(f"Error from ChatFAQ's back-end server: {payload}")

    async def send_rag_request(
        self,
        rag_config_name,
        input_text,
        use_conversation_context,
        only_context,
        conversation_id,
        bot_channel_name,
        user_id=None,
    ):
        logger.info(f"[RAG] Requesting RAG ({rag_config_name})")
        self.llm_request_futures[bot_channel_name] = (
            asyncio.get_event_loop().create_future()
        )
        await getattr(self, f"ws_{WSType.ai.value}").send(
            json.dumps(
                {
                    "type": MessageType.rag_request.value,
                    "data": {
                        "rag_config_name": rag_config_name,
                        "input_text": input_text,
                        "use_conversation_context": use_conversation_context,
                        "conversation_id": conversation_id,
                        "user_id": user_id,
                        "bot_channel_name": bot_channel_name,
                        "only_context": only_context,
                    },
                }
            )
        )

    async def send_llm_request(
            self,
            llm_config_name,
            messages,
            temperature,
            max_tokens,
            seed,
            tools,
            tool_choice,
            conversation_id,
            bot_channel_name,
            use_conversation_context,
    ):
        logger.info(f"[LLM] Requesting LLM ({llm_config_name})")
        self.llm_request_futures[bot_channel_name] = asyncio.get_event_loop().create_future()
        await getattr(self, f"ws_{WSType.ai.value}").send(
            json.dumps(
                {
                    "type": MessageType.llm_request.value,
                    "data": {
                        "llm_config_name": llm_config_name,
                        "messages": messages,
                        "conversation_id": conversation_id,
                        "bot_channel_name": bot_channel_name,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "seed": seed,
                        "tools": tools,
                        "tool_choice": tool_choice,
                        "use_conversation_context": use_conversation_context,
                    },
                }
            )
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
            @wraps(func)
            def inner(sdk: ChatFAQSDK, ctx: dict):
                return func(sdk, ctx)

            if name not in self.rpcs:
                self._rpcs[name] = []
                self.rpcs[name] = []
            if func not in self._rpcs[name]:
                self._rpcs[name].append(func)
                self.rpcs[name].append(inner)

            return inner

        return outer

    async def _run_handler(self, handler, data):
        async_func = handler(self, data)
        if inspect.isasyncgen(async_func):
            is_last = False
            layer = await anext(async_func)

            while not is_last:
                _layer = None
                try:
                    _layer = await anext(async_func)
                except StopAsyncIteration:
                    is_last = True

                async for results in self._layer_results(layer, data):
                    yield [results[0], results[1] and is_last, results[2]]
                layer = _layer
        else:
            layer = await async_func
            async for results in self._layer_results(layer, data):
                yield results

    async def _layer_results(self, layer, data):
        if not isinstance(layer, Layer) and not isinstance(layer, Condition):
            raise Exception(
                "RPCs results should return either Layers type objects or result type objects"
            )
        results = layer.result(self, data)
        # check if is generator
        async for r in results:
            yield r + [
                RPCNodeType.action.value
                if isinstance(layer, Layer)
                else RPCNodeType.condition.value
            ]

    def parsing_wrapper(self, parser):
        async def _parsing_wrapper(payload):
            logger.info(f"[PARSE] Parsing ::: {payload}")
            data_source = DataSource(**payload)

            for ki in parser(data_source.kb_id, data_source.ds_id, data_source):
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        urllib.parse.urljoin(
                            self.chatfaq_http,
                            "back/api/language-model/knowledge-items/",
                        ),
                        json=ki.dict(),
                        headers={"Authorization": f"Token {self.token}"},
                    )
                    response.raise_for_status()
                    ki_res = response.json()
                    if ki.images:
                        for index, ki_image in enumerate(ki.images):
                            ki_image.knowledge_item = ki_res["id"]
                            response = await client.post(
                                urllib.parse.urljoin(
                                    self.chatfaq_http,
                                    "back/api/language-model/knowledge-item-images/",
                                ),
                                data=ki_image.dict(),
                                files=ki_image.files(),
                                headers={"Authorization": f"Token {self.token}"},
                            )
                            response.raise_for_status()
                            ki_image = response.json()
                            ki_res["content"] = ki_res["content"].replace(
                                f"[[Image {index}]]",
                                f"![{ki_image.get('image_caption') or ki_image['image_file_name']}]({ki_image['image_file_name']})",
                            )
                            response = await client.patch(
                                urllib.parse.urljoin(
                                    self.chatfaq_http,
                                    f"back/api/language-model/knowledge-items/{ki_res['id']}/",
                                ),
                                json=ki_res,
                                headers={"Authorization": f"Token {self.token}"},
                            )
                            response.raise_for_status()

            if data_source.task_id:
                await getattr(self, f"ws_{WSType.parse.value}").send(
                    json.dumps(
                        {
                            "type": MessageType.parser_finished.value,
                            "data": {"task_id": data_source.task_id},
                        }
                    )
                )

        return _parsing_wrapper
