from chatfaq_sdk import ChatFAQSDK
from chatfaq_sdk.fsm import FSMDefinition, State, Transition
from chatfaq_sdk.layers import Message


async def send_greeting(sdk: ChatFAQSDK, ctx: dict):
    yield Message("How can we help you?", )


async def send_answer(sdk: ChatFAQSDK, ctx: dict):
    # TODO: Implement the new RAG logic
    pass


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
