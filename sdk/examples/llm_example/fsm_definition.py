from chatfaq_sdk import ChatFAQSDK
from chatfaq_sdk.fsm import FSMDefinition, State, Transition
from chatfaq_sdk.layers import Message, StreamingMessage
from chatfaq_sdk.clients import llm_request
from chatfaq_sdk.utils import convert_mml_to_llm_format


async def send_greeting(sdk: ChatFAQSDK, ctx: dict):
    yield Message("How can we help you?")


async def send_answer(sdk: ChatFAQSDK, ctx: dict):
    # messages = convert_mml_to_llm_format(ctx["conv_mml"][1:]) # skip the greeting message
    # messages.insert(0, {"role": "system", "content": "You are a helpful assistant."})

    generator = llm_request(
        sdk,
        "gpt-4o",
        use_conversation_context=True, # If this is true the backend will send the previous messages to the LLM. Otherwise, the fsm manages the conversation.
        conversation_id=ctx["conversation_id"],
        bot_channel_name=ctx["bot_channel_name"],
        # messages=messages,
        stream=True,
    )

    yield StreamingMessage(generator)


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
