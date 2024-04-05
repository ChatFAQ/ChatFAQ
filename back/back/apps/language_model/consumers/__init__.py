import json
import uuid

import httpx
from logging import getLogger
from django.forms.models import model_to_dict

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

from back.apps.broker.consumers.message_types import RPCMessageType
from back.apps.broker.models.message import Conversation, StackPayloadType, AgentType, Message
from back.apps.broker.serializers.rpc import RPCLLMRequestSerializer
from back.apps.language_model.models import RAGConfig, KnowledgeItem, MessageKnowledgeItem
from back.utils import WSStatusCodes
from back.utils.custom_channels import CustomAsyncConsumer

logger = getLogger(__name__)


def format_msgs_chain_to_llm_context(msgs_chain):
    messages = []
    for msg in msgs_chain:
        if msg.sender["type"] == AgentType.human.value:
            text = ""
            for stack in msg.stack:
                if stack["type"] == StackPayloadType.text.value:
                    text += stack["payload"]
                else:
                    logger.warning(f"Stack type {stack['type']} for sender {msg['sender']['type']} is not supported for LLM contextualization.")

            messages.append({"role": "user", "content": text})
        elif msg.sender["type"] == AgentType.bot.value:
            text = ""
            for stack in msg.stack:
                if stack["type"] == StackPayloadType.lm_generated_text.value:
                    text += stack['payload']['model_response']
                else:
                    logger.warning(f"Stack type {stack['type']} for sender {msg.sender['type']} is not supported for LLM contextualization.")
            messages.append({"role": "assistant", "content": text})

    return messages


async def query_ray(rag_config_name, conversation_id, input_text=None, use_conversation_context=True, streaming=True):
    """
    # for debuggin purposes send 100 messages waiting 0.1 seconds between each one
    import asyncio
    for i in range(100):
        await asyncio.sleep(0.1)
        yield {"model_response": f"Message {i}", "references": {}, "final": False}
    yield {"model_response": "End of messages", "references": {}, "final": True}

    return
    """
    try:
        rag_conf = await database_sync_to_async(RAGConfig.enabled_objects.prefetch_related("prompt_config", "generation_config", "knowledge_base").get)(name=rag_config_name)
    except RAGConfig.DoesNotExist:
        yield {"model_response": f"RAG config with name: {rag_config_name} does not exist.", "references": {}, "final": True}
        return

    p_conf = model_to_dict(rag_conf.prompt_config)
    p_conf.pop("id")
    g_conf = model_to_dict(rag_conf.generation_config)
    g_conf.pop("id")

    conv = await database_sync_to_async(Conversation.objects.get)(pk=conversation_id)
    prev_kis = conv.get_kis()

    messages = ""
    if use_conversation_context:
        messages = format_msgs_chain_to_llm_context(await database_sync_to_async(list)(conv.get_msgs_chain()))
    if input_text:
        messages.append({"role": "user", "content": input_text})

    request_data = {
        "messages": messages,
        "prev_contents": await database_sync_to_async(list)(prev_kis.values_list("content", flat=True)),
        "prompt_structure_dict": p_conf,
        "generation_config_dict": g_conf,
    }

    rag_url = rag_conf.get_ray_endpoint()
    reference_kis = []

    logger.info(f"{'>' * 80}\n"
                f"Input query: {input_text if input_text else messages[-1]['content']}\n"
                f"Prompt config: {p_conf}\n"
                f"Generation config: {g_conf}\n"
                f"Querying RAG {rag_conf.name} at {rag_url}\n"
                f"{'<' * 80}")

    try:
        if streaming:
            async with httpx.AsyncClient() as client:
                async with client.stream('POST', rag_url, json=request_data) as r:
                    r.raise_for_status()
                    async for chunk in r.aiter_bytes():
                        ray_res = json.loads(chunk)
                        yield {"model_response": ray_res.get("res", ""), "references": {}, "final": False}

                        if reference_kis is None:
                            reference_kis = ray_res.get("context", [[]])[0]
        else:
            pass  # TODO: implement non-streaming version
    except Exception as e:
        logger.error("Error during RAG query", exc_info=e)
        # return _send_message(bot_channel_name, lm_msg_id, channel_layer, chanel_name, msg='There was an error generating the response. Please try again or contact the administrator.')
        yield {"model_response": "There was an error generating the response. Please try again or contact the administrator.", "references": {}, "final": True}
        return

    # ColBERT only returns the k item id, similarity and content, so we need to get the full k item fields
    # We also adapt the pgvector retriever to match colbert's output
    for index, ki in enumerate(reference_kis):
        reference_kis[index] = {
            **KnowledgeItem.objects.get(pk=ki['k_item_id']).to_retrieve_context(),
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

    references = {
        "knowledge_base_id": rag_conf.knowledge_base.pk,
        "knowledge_items": reference_kis,
        "knowledge_item_images": reference_ki_images,
    }
    yield {"model_response": "", "references": references, "final": True}

    if not input_text:  # Only when the generated text based on a human message then we will associate the generated text with it
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


class LLMConsumer(CustomAsyncConsumer, AsyncJsonWebsocketConsumer):
    """
    The consumer in responsible for
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
        logger.debug(
            f"Starting new LLM WS connection (channel group: {self.channel_name})"
        )

    async def disconnect(self, close_code):
        logger.debug(f"Disconnecting from LLM consumer {close_code}")

    async def receive_json(self, content, **kwargs):
        serializer = RPCLLMRequestSerializer(data=content)
        if not serializer.is_valid():
            await self.error_response(
                {"payload": {"errors": serializer.errors, "request_info": content}}
            )
            return

        lm_msg_id = str(uuid.uuid4())
        data = serializer.validated_data
        async for chunk in query_ray(data["rag_config_name"], data["conversation_id"], data.get("input_text"), data["use_conversation_context"], data["streaming"]):
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

    async def error_response(self, data: dict):
        data["status"] = WSStatusCodes.bad_request.value
        data["type"] = RPCMessageType.error.value
        await self.send(json.dumps(data))
