from chatfaq_sdk import ChatFAQSDK
from chatfaq_sdk.clients import llm_request
from chatfaq_sdk.fsm import FSMDefinition, State, Transition
from chatfaq_sdk.layers import Message, StreamingMessage, ToolUse, ToolResult
from chatfaq_sdk.utils import convert_mml_to_llm_format


MODEL_NAME = "gemini-2.0-flash"

def get_weather(location: str) -> str:
    """
    Get current temperature for a given location.
    :param location: City and country e.g. Bogotá, Colombia
    :return: Current temperature for the given location
    """
    return f"The temperature in {location} is 20°C"


async def send_greeting(sdk: ChatFAQSDK, ctx: dict):
    yield Message("How can we help you?")


async def send_answer(sdk: ChatFAQSDK, ctx: dict):
    messages = convert_mml_to_llm_format(ctx["conv_mml"][1:]) # skip the greeting message and get the user message
    messages.insert(0, {"role": "system", "content": "You are a knowledgeable weather assistant. Use provided tools when necessary."})

    response = await llm_request(
        sdk,
        MODEL_NAME,
        use_conversation_context=False,
        conversation_id=ctx["conversation_id"],
        bot_channel_name=ctx["bot_channel_name"],
        messages=messages,
        tools=[get_weather],
        tool_choice="auto",
        stream=False, 
    )
    print(response)

    tool_results = []
    for content in response["content"]:
        if content["type"] == "text":
            yield Message(content["text"])
        elif content["type"] == "tool_use":
            yield ToolUse(name=content["tool_use"]["name"], id=content["tool_use"]["id"], args=content["tool_use"]["args"])
            if content["tool_use"]["name"] == "get_weather":
                result = get_weather(content["tool_use"]["args"]["location"])
                yield ToolResult(id=content["tool_use"]["id"], name=content["tool_use"]["name"], result=result)
                tool_results.append(
                    {
                        "id": content["tool_use"]["id"],
                        "name": content["tool_use"]["name"],
                        "result": result
                    }
                )
    
    if tool_results:
        # If there are tool results it means that the model has called a tool
        # so we need to append the tool results to the messages and ask the model to continue
        messages.append({
            "role": "assistant",
            "content": response["content"]
        })
        messages.append({
            "role": "user",
            "content": [{"type": "tool_result", "tool_result": tool_result} for tool_result in tool_results]
        })
        
        response = await llm_request(
            sdk,
            MODEL_NAME,
            messages=messages,
            use_conversation_context=False,
            conversation_id=ctx["conversation_id"],
            bot_channel_name=ctx["bot_channel_name"],
            tools=[get_weather],
            tool_choice="auto",
            stream=False, 
        )
        print(response)
        yield Message(response["content"][0]["text"])



greeting_state = State(name="Greeting", events=[send_greeting], initial=True)

answering_state = State(
    name="Answering",
    events=[send_answer],
)

_to_answer = Transition(
    dest=answering_state,
)

fsm_definition = FSMDefinition(
    states=[greeting_state, answering_state],
    transitions=[_to_answer]
)