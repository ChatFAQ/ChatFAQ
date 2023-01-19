import random

from riddler_sdk.conditions import Result
from riddler_sdk.fsm import State, Transition, FSMDefinition
from riddler_sdk.layers import Text


# TODO: create type out of ctx
# TODO: create type out of this return data structure and check of type on sdk handler registration
def is_saying_goodbye(ctx: dict):
    if ctx["last_mml"]["stacks"][0][0]["payload"] == "goodbye":
        return Result(1)
    return Result(0)


def send_hello(ctx: dict):
    yield Text("Hello!")
    yield Text("How are you?")


def send_answer(ctx: dict):
    last_payload = ctx['last_mml']['stacks'][0][0]['payload']
    yield Text(f'My answer to your message: "{last_payload}" is: {random.randint(0, 999)}')
    yield Text(f'Tell me more')


def send_goodbye(ctx: dict):
    yield Text("Byeeeeeeee!")


hello_state = State(
    name="hello",
    events=[send_hello],
    initial=True
)

answering_state = State(
    name="answering",
    events=[send_answer],
)

goodbye_state = State(
    name="goodbye",
    events=[send_goodbye],
)

hello_to_answer = Transition(
    source=hello_state,
    dest=answering_state,
)
answer_to_answer = Transition(
    source=answering_state,
    dest=answering_state,
    unless=[is_saying_goodbye]
)
any_to_goodbye = Transition(
    dest=goodbye_state,
    conditions=[is_saying_goodbye]
)

fsm_def = FSMDefinition(
    states=[hello_state, answering_state, goodbye_state],
    transitions=[hello_to_answer, answer_to_answer, any_to_goodbye],
)
