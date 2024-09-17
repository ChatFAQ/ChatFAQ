from typing import Dict, List
from pydantic import BaseModel
from logging import getLogger
from chatfaq_sdk import ChatFAQSDK


logger = getLogger(__name__)

async def llm_request(
    sdk: ChatFAQSDK,
    llm_config_name: str,
    messages: List[Dict[str, str]] = None,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    seed: int = 42,
    tools: List[BaseModel] = None,
    tool_choice: str = None,
    conversation_id: str = None,
    bot_channel_name: str = None,
    use_conversation_context: bool = True,
):
    if tools:
        tools = [tool.model_json_schema() for tool in tools]

    await sdk.send_llm_request(
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
    )

    logger.debug("[LLMRequest] Waiting for LLM req...")
    final = False
    while not final:
        results = (await sdk.llm_request_futures[bot_channel_name])()
        logger.debug("[LLMRequest] ...receive results from LLM req")

        for result in results:
            final = result.get("last_chunk", False)
            yield result
        logger.debug(f"[LLMRequest] (Final: {final})")


async def retrieve(
    sdk: ChatFAQSDK,
    retriever_name: str,
    query: str,
    top_k: int,
    bot_channel_name: str,
):
    await sdk.send_retriever_request(retriever_name, query, top_k, bot_channel_name)

    logger.debug("[Retrieve] Waiting for Retrieve req...")
    results = await sdk.retriever_request_futures[bot_channel_name]
    logger.debug("[Retrieve] ...receive results from Retrieve req")

    return results


async def get_prompt(
    sdk: ChatFAQSDK,
    prompt_config_name: str,
    bot_channel_name: str,
):
    await sdk.send_prompt_request(prompt_config_name, bot_channel_name)

    logger.debug("[Prompt] Waiting for Prompt req...")
    results = await sdk.prompt_request_futures[bot_channel_name]
    logger.debug("[Prompt] ...receive results from Prompt req")
    return results