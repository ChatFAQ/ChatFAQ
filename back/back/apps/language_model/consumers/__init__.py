import json
import uuid
from logging import getLogger
from typing import Dict, List

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from ray.serve import get_deployment_handle

from back.apps.broker.consumers.message_types import RPCMessageType
from back.apps.broker.models.message import AgentType, Conversation, StackPayloadType
from back.apps.broker.serializers.rpc import (
    RPCLLMRequestSerializer,
    RPCRetrieverRequestSerializer,
    RPCResponseSerializer,
)
from back.apps.language_model.models import (
    KnowledgeItem,
    LLMConfig,
    RetrieverConfig,
)
from back.utils import WSStatusCodes
from back.utils.custom_channels import CustomAsyncConsumer

logger = getLogger(__name__)


def format_msgs_chain_to_llm_context(msgs_chain, message_types: List[str]) -> List[Dict[str, str]]:
    """
    Returns a list of messages using the OpenAI standard format for LLMs.
    Parameters
    ----------
    msgs_chain :
        A list of messages in the broker format.
    message_types : List[str]
        The types of messages to extract from the broker message stack.
    """
    messages = []
    for msg in msgs_chain:
        if msg.sender["type"] == AgentType.human.value:
            text = ""
            for stack in msg.stack:
                if stack["type"] in message_types:
                    text += stack["payload"]["content"]
                else:
                    logger.warning(
                        f"Stack type {stack['type']} for sender {msg['sender']['type']} is not supported for LLM contextualization."
                    )

            if text:
                messages.append({"role": "user", "content": text})
        elif msg.sender["type"] == AgentType.bot.value:
            text = ""
            for stack in msg.stack:
                if stack["type"] in message_types:
                    text += stack["payload"]["content"]
                else:
                    logger.warning(
                        f"Stack type {stack['type']} for sender {msg.sender['type']} is not supported for LLM contextualization."
                    )
            if text:
                messages.append({"role": "assistant", "content": text})

    return messages


async def resolve_references(reference_kis, retriever_config):
    # ColBERT only returns the k item id, similarity and content, so we need to get the full k item fields
    # We also adapt the pgvector retriever to match colbert's output

    for index, ki in enumerate(reference_kis):
        ki_item = await database_sync_to_async(
            KnowledgeItem.objects.prefetch_related("knowledgeitemimage_set").get
        )(pk=ki["k_item_id"])
        reference_kis[index] = {
            **ki_item.to_retrieve_context(),
            "similarity": ki["similarity"],
        }

    logger.info(f"References:\n{reference_kis}")
    # All images of the conversation so far
    reference_ki_images = {}
    for reference_ki in reference_kis:
        reference_ki_images = {**reference_ki_images, **reference_ki["image_urls"]}

    # TODO: We no longer associate the knowledge items with messages, in the future we will modify this
    # TODO: to associate the query with the knowledge items and the retriever used.
    # if relate_kis_to_msgs:  # Only when the generated text based on a human message then we will associate the generated text with it
    #     last_human_mml = await database_sync_to_async(conv.get_last_human_mml)()
    #     msgs2kis = [
    #         MessageKnowledgeItem(
    #             message=last_human_mml,
    #             knowledge_item_id=ki["knowledge_item_id"],
    #             similarity=ki["similarity"],
    #         )
    #         for ki in reference_kis
    #     ]
    #     await database_sync_to_async(MessageKnowledgeItem.objects.bulk_create)(msgs2kis)

    return {
        "knowledge_base_id": await database_sync_to_async(lambda: retriever_config.knowledge_base.pk)(),
        "knowledge_items": reference_kis,
        "knowledge_item_images": reference_ki_images,
    }


async def query_llm(
    llm_config_name: str,
    conversation_id: int,
    messages: List[Dict[str, str]] = None,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    seed: int = 42,
    tools: List[Dict] = None,
    tool_choice: str = None,
    streaming: bool = True,
    use_conversation_context: bool = True,
):
    try:
        llm_config = await database_sync_to_async(LLMConfig.enabled_objects.get)(
            name=llm_config_name
        )
    except LLMConfig.DoesNotExist:
        yield {
            "content": f"LLM config with name: {llm_config_name} does not exist.",
            "final": True,
        }
        return

    conv = await database_sync_to_async(Conversation.objects.get)(pk=conversation_id)
    
    if use_conversation_context:
        prev_messages = format_msgs_chain_to_llm_context(
            await database_sync_to_async(list)(conv.get_msgs_chain()), [StackPayloadType.message.value, StackPayloadType.message_chunk.value]
        )
        new_messages = prev_messages.copy()

        if messages: # In case the fsm sends messages
            if messages[0]["role"] == "system":
                if prev_messages[0]["role"] == "system":
                    new_messages[0] = messages[0]  # replace the original system message with the new one from the fsm
                else:
                    new_messages.insert(0, messages[0])  # or add the fsm system message

                # pop the system message
                messages = messages[1:]

        new_messages.extend(messages)
    else:
        new_messages = messages

    try:
        if streaming:
            llm_deploy_name = llm_config.get_deploy_name()
            handle = get_deployment_handle(
                deployment_name=llm_deploy_name, app_name=llm_deploy_name
            ).options(stream=True)

            response = handle.remote(
                new_messages,
                temperature,
                max_tokens,
                seed,
                tools,
                tool_choice
            )

            async for res in response:
                # if res is a list then it's a tool response and it's not streamed, it returns the full response
                if isinstance(res, list):
                    yield {
                        "content": "",
                        "tool_use": res,
                        "final": True,
                    }
                    return


                yield {
                    "content": res,
                    "final": False,
                }

            yield {
                "content": "",
                "final": True,
            }

        else:
            pass

    except Exception as e:
        logger.error("Error during LLM query", exc_info=e)
        yield {
            "content": "There was an error generating the response. Please try again or contact the administrator.",
            "final": True,
        }
        return


async def query_retriever(
    retriever_config_name: str,
    query: str,
    top_k: int,
):
    try:
        retriever_config = await database_sync_to_async(RetrieverConfig.enabled_objects.get)(
            name=retriever_config_name
        )
    except RetrieverConfig.DoesNotExist:
        return {
            "content": f"Retriever config with name: {retriever_config_name} does not exist.",
            "final": True,
        }

    try:
        retriever_deploy_name = retriever_config.get_deploy_name()
        handle = get_deployment_handle(
            deployment_name=retriever_deploy_name, app_name=retriever_deploy_name
        )

        result = await handle.remote(query, top_k)
        result = await resolve_references(result, retriever_config)

        return result
    
    except Exception as e:
        logger.error("Error while querying the retriever", exc_info=e)
        return {
            "error": True,
        }


class AIConsumer(CustomAsyncConsumer, AsyncJsonWebsocketConsumer):
    """
    The consumer in responsible for handling all the AI requests from the SDK, for now only calling a LLM.
    """

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
            return
        await self.accept()
        print(f"Starting new LLM WS connection (channel group: {self.channel_name})")

    async def disconnect(self, close_code):
        print(f"Disconnecting from LLM consumer {close_code}")

    async def receive_json(self, content, **kwargs):
        serializer = RPCResponseSerializer(data=content)

        if not serializer.is_valid():
            await self.error_response(
                {"payload": {"errors": serializer.errors, "request_info": content}}
            )
            return

        if serializer.validated_data["type"] == RPCMessageType.llm_request.value:
            await self.process_llm_request(serializer.validated_data["data"])
        elif serializer.validated_data["type"] == RPCMessageType.retriever_request.value:
            await self.process_retriever_request(serializer.validated_data["data"])

    async def process_llm_request(self, data):
        serializer = RPCLLMRequestSerializer(data=data)
        if not serializer.is_valid():
            await self.error_response(
                {"payload": {"errors": serializer.errors, "request_info": data}}
            )
            return

        lm_msg_id = str(uuid.uuid4())
        data = serializer.validated_data
        async for chunk in query_llm(
            data["llm_config_name"],
            data["conversation_id"],
            data["messages"],
            data.get("temperature"),
            data.get("max_tokens"),
            data.get("seed"),
            data.get("tools"),
            data.get("tool_choice"),
            data.get("streaming"),
            data.get("use_conversation_context"),
        ):
            await self.send(
                json.dumps(
                    {
                        "type": RPCMessageType.llm_request_result.value,
                        "status": WSStatusCodes.ok.value,
                        "payload": {
                            **chunk,
                            "bot_channel_name": data["bot_channel_name"],
                            "lm_msg_id": lm_msg_id,
                        },
                    }
                )
            )

    async def process_retriever_request(self, data):
        serializer = RPCRetrieverRequestSerializer(data=data)
        if not serializer.is_valid():
            await self.error_response(
                {"payload": {"errors": serializer.errors, "request_info": data}}
            )
            return
        
        data = serializer.validated_data
        result = await query_retriever(
            data["retriever_config_name"],
            data["query"],
            data.get("top_k"),
        )

        if result.get("error"):
            await self.error_response(
                {
                    "payload": {
                        "errors": result,
                        "request_info": data,
                    }
                }
            )
            return

        await self.send(
            json.dumps(
                {
                    "type": RPCMessageType.retriever_request_result.value,
                    "status": WSStatusCodes.ok.value,
                    "payload": {
                        "k_items": result,
                        "bot_channel_name": data["bot_channel_name"],
                    },
                }
            )
        )

    async def error_response(self, data: dict):
        data["status"] = WSStatusCodes.bad_request.value
        data["type"] = RPCMessageType.error.value
        await self.send(json.dumps(data))
