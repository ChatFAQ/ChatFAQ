import json
import uuid
from logging import getLogger
from typing import Dict, List, Optional

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from ray.serve import get_deployment_handle

from back.apps.broker.consumers.message_types import RPCMessageType
from back.apps.broker.models.message import AgentType, Conversation
from back.apps.broker.serializers.rpc import (
    RPCLLMRequestSerializer,
    RPCPromptRequestSerializer,
    RPCResponseSerializer,
    RPCRetrieverRequestSerializer,
)
from back.apps.language_model.models import (
    KnowledgeItem,
    LLMConfig,
    PromptConfig,
    RetrieverConfig,
)
from back.config import settings
from back.utils import WSStatusCodes
from back.utils.custom_channels import CustomAsyncConsumer
from chat_rag.llms import load_llm
from chat_rag.llms.types import Content, Message, ToolResult, ToolUse

logger = getLogger(__name__)


def format_msgs_chain_to_llm_context(msgs_chain) -> List[Message]:
    """
    Returns a list of chat_rag Message objects representing the conversation context.
    Consecutive messages coming from the same sender type are concatenated into one Message.
    The content of each Message is a list of chat_rag Content objects, which can include plain text,
    tool calls (tool_use) and tool results (tool_result).

    Parameters
    ----------
    msgs_chain :
        A list of messages in the broker format.
        
    Returns
    -------
    List[Message]
        A list of chat_rag Message objects with messages concatenated by sender.
    """
    aggregated_messages = []
    current_role = None  # "user" for human and "assistant" for bot
    aggregated_contents = []  # list of Content objects for the current group

    def process_stack(stack) -> List[Content]:
        """
        Process a single stack item into a list of chat_rag Content objects.
        It checks for text content, tool calls, and tool results.
        """
        contents = []
        payload = stack.get("payload", {})
        type = stack.get("type")

        # Create a text content if available.
        if type == "message":
            contents.append(Content(text=payload.get("content"), type="text"))

        # Check if this stack represents a tool call (tool use).
        if type == "tool_use":
            tool_use_obj = ToolUse(**payload)
            contents.append(Content(tool_use=tool_use_obj, type="tool_use"))

        # Check if this stack represents a tool result.
        if type == "tool_result":
            tool_result_obj = ToolResult(**payload)
            contents.append(Content(tool_result=tool_result_obj, type="tool_result"))

        return contents

    def process_msg(msg) -> List[Content]:
        """
        Process each broker message into a list of chat_rag Content objects by iterating over its stacks.
        """
        contents = []
        for stack in msg.stack:
            contents.extend(process_stack(stack))
        return contents

    def merge_contents(existing: List[Content], new: List[Content]) -> List[Content]:
        """
        Merge two lists of chat_rag Content objects.
        If the last element of the existing list and the first element of the new list are both text,
        then they are concatenated.
        """
        if not existing:
            return new
        if not new:
            return existing

        merged = existing.copy()
        # If the last and first items are text, merge them.
        if merged and new and merged[-1].type == "text" and new[0].type == "text":
            merged[-1].text = merged[-1].text.strip() + " " + new[0].text.strip()
            merged.extend(new[1:])
        else:
            merged.extend(new)
        return merged

    # Iterate over each message in the msgs_chain, grouping contiguous messages by sender type.
    for msg in msgs_chain:
        # Map sender type to LLM context role.
        sender_type = msg.sender.get("type")
        if sender_type == AgentType.human.value:
            role = "user"
        elif sender_type == AgentType.bot.value:
            role = "assistant"
        else:
            # Skip messages that are not from a human or bot.
            continue

        # Process the message stacks to obtain its list of Content objects.
        msg_contents = process_msg(msg)
        if not msg_contents:
            continue

        if current_role is None:
            # Start a new group.
            current_role = role
            aggregated_contents = msg_contents
        elif current_role == role:
            # Same role: merge new contents with the existing group.
            aggregated_contents = merge_contents(aggregated_contents, msg_contents)
        else:
            # Role changed, so package the current group into a Message.
            aggregated_messages.append(
                Message(
                    role=current_role,
                    content=aggregated_contents,
                    usage=None,
                    stop_reason="end_turn"
                )
            )
            # Start a new group for the new role.
            current_role = role
            aggregated_contents = msg_contents

    # Append any remaining aggregated messages.
    if current_role is not None and aggregated_contents:
        aggregated_messages.append(
            Message(
                role=current_role,
                content=aggregated_contents,
                usage=None,
                stop_reason="end_turn"
            )
        )

    return aggregated_messages


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
    messages: List[Dict] = None,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    seed: int = 42,
    tools: List[Dict] = None,
    tool_choice: str = None,
    use_conversation_context: bool = True,
    cache_config: Optional[Dict] = None,
    stream: bool = False,
):
    try:
        llm_config = await database_sync_to_async(LLMConfig.enabled_objects.get)(
            name=llm_config_name
        )
    except LLMConfig.DoesNotExist:
        yield {
            "content": [{"type": "text", "text": f"LLM config with name: {llm_config_name} does not exist."}],
            "last_chunk": True,
        }
        return

    conv = await database_sync_to_async(Conversation.objects.get)(pk=conversation_id)

    if use_conversation_context:
        prev_messages = format_msgs_chain_to_llm_context(
            await database_sync_to_async(list)(conv.get_msgs_chain())
        )
        new_messages = prev_messages.copy()

        if messages: # In case the fsm sends messages
            if messages[0]["role"] == AgentType.system.value:
                if prev_messages[0].role == AgentType.system.value:
                    new_messages[0] = Message(**messages[0])  # replace the original system message with the new one from the fsm
                else:
                    new_messages.insert(0, Message(**messages[0]))  # or add the fsm system message

                # pop the system message
                messages = messages[1:]
        elif not prev_messages:
            yield {
                "content": [
                    {
                        "type": "text",
                        "text": "Error: No previous messages and no messages provided.",
                    }
                ],
                "last_chunk": True,
            }
            return
        if messages:
            new_messages.extend(messages)
    else:
        new_messages = messages
        if new_messages is None:
            yield {
                "content": [{"type": "text", "text": "Error: No messages provided."}],
                "last_chunk": True,
            }
            return

    try:
        # Decrypt the API key from the LLMConfig if available.
        api_key = None
        if llm_config.api_key:
            from back.utils.encrypt import get_light_bringer
            lb = get_light_bringer()
            api_key = llm_config.api_key.decrypt(lb)

        # Now pass the decrypted API key into the LLM.
        llm = load_llm(
            llm_config.llm_type,
            llm_config.llm_name,
            base_url=llm_config.base_url,
            model_max_length=llm_config.model_max_length,
            api_key=api_key,
        )
        # chat_rag models don't support streaming when using tools
        if stream and not tools:
            response = llm.astream(
                messages=new_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                seed=seed,
                cache_config=cache_config,
            )
            async for res in response:
                yield {
                    "content": res,
                    "last_chunk": False,
                }
            yield {
                "content": "",
                "last_chunk": True,
            }

        else:
            response_message = await llm.agenerate(
                messages=new_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                seed=seed,
                tools=tools,
                tool_choice=tool_choice,
                cache_config=cache_config,
            )
            yield {
                "content": [content.model_dump() for content in response_message.content], # Make it serializable
                "usage": response_message.usage.model_dump(),
                "stop_reason": response_message.stop_reason,
                "last_chunk": True,
            }

    except Exception as e:
        logger.error("Error during LLM query", exc_info=e)
        yield {
            "content": [{"type": "text", "text": "There was an error generating the response. Please try again or contact the administrator."}],
            "last_chunk": True,
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
            "last_chunk": True,
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
        elif serializer.validated_data["type"] == RPCMessageType.prompt_request.value:
            await self.process_prompt_request(serializer.validated_data["data"])

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
            data.get("use_conversation_context"),
            data.get("cache_config"),
            data.get("stream"),
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
                        **result,
                        "bot_channel_name": data["bot_channel_name"],
                    },
                }
            )
        )

    async def process_prompt_request(self, data):
        serializer = RPCPromptRequestSerializer(data=data)
        if not serializer.is_valid():
            await self.error_response(
                {"payload": {"errors": serializer.errors, "request_info": data}}
            )
            return

        data = serializer.validated_data

        try:
            prompt_config = await database_sync_to_async(PromptConfig.objects.get)(
                name=data["prompt_config_name"]
            )
            await self.send(
                json.dumps(
                    {
                        "type": RPCMessageType.prompt_request_result.value,
                        "status": WSStatusCodes.ok.value,
                        "payload": {
                            "prompt": prompt_config.prompt,
                            "bot_channel_name": data["bot_channel_name"],
                        },
                    }
                )
            )

        except PromptConfig.DoesNotExist:
            await self.error_response(
                {
                    "payload": {
                        "errors": f"Prompt config with name: {data['prompt_config_name']} does not exist.",
                        "request_info": data,
                    }
                }
            )



    async def error_response(self, data: dict):
        data["status"] = WSStatusCodes.bad_request.value
        data["type"] = RPCMessageType.error.value
        await self.send(json.dumps(data))
