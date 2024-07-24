from typing import Dict, List

from pydantic import BaseModel
from logging import getLogger

from chatfaq_sdk import ChatFAQSDK

logger = getLogger(__name__)


class BackendClient:
    def __init__(self, sdk: ChatFAQSDK):
        self.sdk = sdk

    async def req(
        self,
        llm_config_name,
        messages: List[Dict[str, str]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        seed: int = 42,
        tools: List[BaseModel] = None,
        tool_choice: str = None,
        conversation_id: str = None,
        bot_channel_name: str = None,
    ):
        self.llm_config_name = llm_config_name
        self.messages = messages
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.seed = seed
        self.tools = tools
        self.tool_choice = tool_choice

        if tools:
            tools = [tool.model_json_schema() for tool in tools]

        await self.sdk.send_llm_request(
            llm_config_name,
            messages,
            temperature,
            max_tokens,
            seed,
            tools,
            tool_choice,
            conversation_id,
            bot_channel_name,
        )

        logger.debug("[BackClient] Waiting for LLM req...")
        final = False
        while not final:
            results = (await self.sdk.llm_request_futures[bot_channel_name])()
            logger.debug(f"[BackClient] ...receive results from LLM req")

            for result in results:
                final = result.get("final", False)
                yield result
            logger.debug(f"[BackClient] (Final: {final})")
