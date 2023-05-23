import random

from chatfaq_sdk.fsm import FSMDefinition, State, Transition
from chatfaq_sdk.layers import LMGeneratedText, Text


def send_greeting(ctx: dict):
    yield Text("Hello!")
    yield Text("How are you?")


def send_answer(ctx: dict):
    last_payload = ctx["last_mml"]["stacks"][0][0]["payload"]
    yield LMGeneratedText(last_payload, 1)
    yield Text(f"Tell me more")


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
    transitions=[_to_answer],
)
