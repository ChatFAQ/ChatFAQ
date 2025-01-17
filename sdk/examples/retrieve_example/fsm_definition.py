from chatfaq_sdk import ChatFAQSDK
from chatfaq_sdk.fsm import FSMDefinition, State, Transition
from chatfaq_sdk.layers import Message
from chatfaq_sdk.clients import retrieve


async def send_greeting(sdk: ChatFAQSDK, ctx: dict):
    yield Message("How can we help you?", )


async def send_answer(sdk: ChatFAQSDK, ctx: dict):
    results = await retrieve(sdk, 'active_seed_e5_small', 'Pure ActiveSeed?', top_k=3, bot_channel_name=ctx["bot_channel_name"])

    yield Message(
        'This is a test',
        references=results,
    )


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
