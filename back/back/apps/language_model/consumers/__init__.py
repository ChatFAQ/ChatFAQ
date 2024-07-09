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
    RPCRAGRequestSerializer,
    RPCResponseSerializer,
)
from back.apps.language_model.models import (
    KnowledgeItem,
    LLMConfig,
    MessageKnowledgeItem,
    RAGConfig,
)
from back.utils import WSStatusCodes
from back.utils.custom_channels import CustomAsyncConsumer

logger = getLogger(__name__)


def format_msgs_chain_to_llm_context(msgs_chain, message_type: str) -> List[Dict[str, str]]:
    """
    Returns a list of messages using the OpenAI standard format for LLMs.
    Parameters
    ----------
    msgs_chain :
        A list of messages in the broker format.
    message_type : str
        The type of message to extract from the broker message stack.
    """
    messages = []
    for msg in msgs_chain:
        if msg.sender["type"] == AgentType.human.value:
            text = ""
            for stack in msg.stack:
                if stack["type"] == StackPayloadType.text.value:
                    text += stack["payload"]
                else:
                    logger.warning(
                        f"Stack type {stack['type']} for sender {msg['sender']['type']} is not supported for LLM contextualization."
                    )

            if text:
                messages.append({"role": "user", "content": text})
        elif msg.sender["type"] == AgentType.bot.value:
            text = ""
            for stack in msg.stack:
                if stack["type"] == message_type:
                    text += stack["payload"]["model_response"]
                else:
                    logger.warning(
                        f"Stack type {stack['type']} for sender {msg.sender['type']} is not supported for LLM contextualization."
                    )
            if text:
                messages.append({"role": "assistant", "content": text})

    return messages


async def resolve_references(reference_kis, conv, rag_conf, relate_kis_to_msgs=False):
    # ColBERT only returns the k item id, similarity and content, so we need to get the full k item fields
    # We also adapt the pgvector retriever to match colbert's output
    prev_kis = await database_sync_to_async(conv.get_kis)()

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
    for ki in await database_sync_to_async(list)(prev_kis):
        for ki_img in await database_sync_to_async(ki.knowledgeitemimage_set.all)():
            reference_ki_images[ki_img.image_file.name] = ki_img.image_file.url

    if relate_kis_to_msgs:  # Only when the generated text based on a human message then we will associate the generated text with it
        last_human_mml = await database_sync_to_async(conv.get_last_human_mml)()
        msgs2kis = [
            MessageKnowledgeItem(
                message=last_human_mml,
                knowledge_item_id=ki["knowledge_item_id"],
                similarity=ki["similarity"],
            )
            for ki in reference_kis
        ]
        await database_sync_to_async(MessageKnowledgeItem.objects.bulk_create)(msgs2kis)

    return {
        "knowledge_base_id": rag_conf.knowledge_base.pk,
        "knowledge_items": reference_kis,
        "knowledge_item_images": reference_ki_images,
    }


async def query_llm(
    llm_config_name: str,
    conversation_id: int,
    messages: List[Dict[str, str]],
    temperature: float = 0.7,
    max_tokens: int = 1024,
    seed: int = 42,
    streaming: bool = True,
):
    try:
        llm_config = await database_sync_to_async(LLMConfig.enabled_objects.get)(
            name=llm_config_name
        )
    except LLMConfig.DoesNotExist:
        yield {
            "model_response": f"LLM config with name: {llm_config_name} does not exist.",
            "final": True,
        }
        return

    conv = await database_sync_to_async(Conversation.objects.get)(pk=conversation_id)
    prev_messages = format_msgs_chain_to_llm_context(
        await database_sync_to_async(list)(conv.get_msgs_chain(), StackPayloadType.llm_generated_text.value)
    )
    new_messages = prev_messages.copy()

    if messages[0]["role"] == "system":
        if prev_messages[0]["role"] == "system":
            new_messages[0] = messages[0]  # replace the system message
        else:
            new_messages.insert(0, messages[0])  # add the system message

        # pop the system message
        messages = messages[1:]

    new_messages.extend(messages)

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
            )

            async for res in response:
                yield {
                    "model_response": res,
                    "final": False,
                }

            yield {
                "model_response": "",
                "final": True,
            }

        else:
            pass

    except Exception as e:
        logger.error("Error during LLM query", exc_info=e)
        yield {
            "model_response": "There was an error generating the response. Please try again or contact the administrator.",
            "final": True,
        }
        return


async def query_rag(
    rag_config_name,
    conversation_id,
    input_text=None,
    use_conversation_context=True,
    only_context=False,
    streaming=True,
):
    """
    # for debuggin purposes send 100 messages waiting 0.1 seconds between each one
    import asyncio
    for i in range(200):
        await asyncio.sleep(0.01)
        yield {"model_response": f"Message {i}", "references": {}, "final": False}
    yield {"model_response": "End of messages", "references": {}, "final": True}

    return
    """
    try:
        rag_conf = await database_sync_to_async(
            RAGConfig.enabled_objects.prefetch_related(
                "prompt_config", "generation_config", "knowledge_base"
            ).get
        )(name=rag_config_name)
    except RAGConfig.DoesNotExist:
        yield {
            "model_response": f"RAG config with name: {rag_config_name} does not exist.",
            "references": {},
            "final": True,
        }
        return

    p_conf = rag_conf.prompt_config
    system_prompt = p_conf.system_prompt
    n_contexts_to_use = p_conf.n_contexts_to_use
    g_conf = rag_conf.generation_config
    temperature = g_conf.temperature
    max_tokens = g_conf.max_tokens
    seed = g_conf.seed

    conv = await database_sync_to_async(Conversation.objects.get)(pk=conversation_id)
    prev_kis = await database_sync_to_async(conv.get_kis)()

    messages = ""
    if use_conversation_context:
        messages = format_msgs_chain_to_llm_context(
            await database_sync_to_async(list)(conv.get_msgs_chain()),
            StackPayloadType.rag_generated_text.value,
        )
    if input_text:
        messages.append({"role": "user", "content": input_text})

    messages.insert(0, {"role": "system", "content": system_prompt})

    references = None

    try:
        if streaming:
            handle = get_deployment_handle(
                "rag_orchestrator", app_name=rag_conf.get_deploy_name()
            ).options(stream=True)
            response = handle.remote(
                messages,
                await database_sync_to_async(list)(
                    prev_kis.values_list("content", flat=True)
                ),
                temperature,
                max_tokens,
                seed,
                n_contexts_to_use,
                only_context,
            )
            async for ray_res in response:
                ray_res = json.loads(ray_res)
                if references is None:
                    references = await resolve_references(
                        (ray_res.get("context", [[]]) or [[]])[0],
                        conv,
                        rag_conf,
                        relate_kis_to_msgs=not input_text,
                    )

                    logger.info(
                        f"{'#' * 80}\n" f"References: {references}\n" f"{'#' * 80}"
                    )

                yield {
                    "model_response": ray_res.get("res", ""),
                    "references": references,
                    "final": False,
                }
        else:
            pass  # TODO: implement non-streaming version
    except Exception as e:
        logger.error("Error during RAG query", exc_info=e)
        # return _send_message(bot_channel_name, lm_msg_id, channel_layer, chanel_name, msg='There was an error generating the response. Please try again or contact the administrator.')
        yield {
            "model_response": "There was an error generating the response. Please try again or contact the administrator.",
            "references": {},
            "final": True,
        }
        return

    yield {"model_response": "", "references": references, "final": True}


class AIConsumer(CustomAsyncConsumer, AsyncJsonWebsocketConsumer):
    """
    The consumer in responsible for handling all the AI requests from the SDK, for now only calling a LLM or RAG.
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

        if serializer.validated_data["type"] == RPCMessageType.rag_request.value:
            await self.process_rag_request(serializer.validated_data["data"])
        elif serializer.validated_data["type"] == RPCMessageType.llm_request.value:
            await self.process_llm_request(serializer.validated_data["data"])

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
            data.get("streaming"),
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

    async def process_rag_request(self, data):
        serializer = RPCRAGRequestSerializer(data=data)
        if not serializer.is_valid():
            await self.error_response(
                {"payload": {"errors": serializer.errors, "request_info": data}}
            )
            return

        lm_msg_id = str(uuid.uuid4())
        data = serializer.validated_data
        async for chunk in query_rag(
            data["rag_config_name"],
            data["conversation_id"],
            data.get("input_text"),
            data["use_conversation_context"],
            data.get("only_context"),
            data["streaming"],
        ):
            await self.send(
                json.dumps(
                    {
                        "type": RPCMessageType.rag_request_result.value,
                        "status": WSStatusCodes.ok.value,
                        "payload": {
                            **chunk,
                            "bot_channel_name": data["bot_channel_name"],
                            "lm_msg_id": lm_msg_id,
                        },
                    }
                )
            )

    async def error_response(self, data: dict):
        data["status"] = WSStatusCodes.bad_request.value
        data["type"] = RPCMessageType.error.value
        await self.send(json.dumps(data))
