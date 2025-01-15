from chatfaq_sdk import ChatFAQSDK
from chatfaq_sdk.fsm import FSMDefinition, State, Transition
from chatfaq_sdk.layers import Message, StarRating, TextFeedback


async def send_greeting(sdk: ChatFAQSDK, ctx: dict):
    yield Message(content="Write a message", allow_feedback=False)


async def send_answer(sdk: ChatFAQSDK, ctx: dict):
    yield Message(content="Some response", allow_feedback=False)
    yield StarRating(content="Please rate the service", num_stars=5, explanation="1 is negative, 5 is positive", allow_feedback=False)
    yield TextFeedback(content="Could you please provide more details?", hint="Please provide your feedback here", allow_feedback=False)


greeting_state = State(name="Greeting", events=[send_greeting], initial=True)

answering_state = State(
    name="Answering",
    events=[send_answer],
)

_to_answer = Transition(
    source=greeting_state,
    dest=answering_state,
)

fsm_definition = FSMDefinition(
    states=[greeting_state, answering_state],
    transitions=[_to_answer]
)
