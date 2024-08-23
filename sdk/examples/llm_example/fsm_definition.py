from chatfaq_sdk import ChatFAQSDK
from chatfaq_sdk.fsm import FSMDefinition, State, Transition
from chatfaq_sdk.layers import Message, StreamingMessage
from chatfaq_sdk.clients import llm_request


async def send_greeting(sdk: ChatFAQSDK, ctx: dict):
    yield Message("How can we help you?", allow_feedback=False)


async def send_answer(sdk: ChatFAQSDK, ctx: dict):
    
    generator = llm_request(
        sdk,
        "gpt-4o",
        use_conversation_context=True,
        conversation_id=ctx["conversation_id"],
        bot_channel_name=ctx["bot_channel_name"],
        messages=[{"role": "system", "content": "You are a helpful assistant."}],
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
