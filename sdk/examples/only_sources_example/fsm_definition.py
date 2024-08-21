from chatfaq_sdk import ChatFAQSDK
from chatfaq_sdk.fsm import FSMDefinition, State, Transition
from chatfaq_sdk.layers import RAGGeneratedText, Message


async def send_greeting(sdk: ChatFAQSDK, ctx: dict):
    yield Message("How can we help you?", allow_feedback=False)


async def send_answer(sdk: ChatFAQSDK, ctx: dict):
    yield RAGGeneratedText("default", only_context=True)


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
