import inspect
from typing import Dict
from chatfaq_sdk import ChatFAQSDK
from chatfaq_sdk.clients import llm_request
from chatfaq_sdk.layers import Message, ToolUse, ToolResult
from chatfaq_sdk.utils import convert_mml_to_llm_format


class Agent:
    """
    An agent that uses the ChatFAQ SDK to interact with an LLM.

    The agent takes a list of tools and a system instruction, and uses them to generate responses to user messages.
    It streams messages, tool uses, and tool results.
    """
    def __init__(self, sdk: ChatFAQSDK, model_name: str, tools: list, system_instruction: str = None):
        self.sdk = sdk
        self.tools = tools
        self.system_instruction = system_instruction
        self.model_name = model_name

    async def run(self, ctx: dict, thinking: str | Dict = None, temperature: float = 0.7, max_tokens: int = 4096):
        messages = convert_mml_to_llm_format(ctx["conv_mml"][1:])  # Skip the greeting message
        if self.system_instruction:
            messages.insert(0, {"role": "system", "content": self.system_instruction})

        while True:
            response = await llm_request(
                self.sdk,
                self.model_name,
                use_conversation_context=False,
                conversation_id=ctx["conversation_id"],
                bot_channel_name=ctx["bot_channel_name"],
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
                stream=False,
                thinking=thinking,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            tool_results = []
            for content in response["content"]:
                if content["type"] == "text":
                    yield Message(content["text"])
                elif content["type"] == "tool_use":
                    tool_use = content["tool_use"]
                    yield ToolUse(name=tool_use["name"], id=tool_use["id"], args=tool_use["args"])
                    # Find the corresponding tool
                    tool = next(t for t in self.tools if t.__name__ == tool_use["name"])
                    # Execute the tool
                    try:
                        if inspect.iscoroutinefunction(tool):
                            result = await tool(**tool_use["args"])
                        else:
                            result = tool(**tool_use["args"])
                    except Exception as e:
                        result = f"Error executing tool {tool_use['name']}: {str(e)}"
                    yield ToolResult(id=tool_use["id"], name=tool_use["name"], result=result)
                    tool_results.append({
                        "id": tool_use["id"],
                        "name": tool_use["name"],
                        "result": result
                    })
            if not tool_results:
                break
            # Append assistant and user messages for the next iteration
            messages.append({
                "role": "assistant",
                "content": response["content"]
            })
            messages.append({
                "role": "user",
                "content": [{"type": "tool_result", "tool_result": tr} for tr in tool_results]
            })