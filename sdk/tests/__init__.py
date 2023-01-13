import random
from riddler_sdk import RiddlerSDK
from riddler_sdk.layers import Text
from tests.fsm_def import fsm_def

sdk = RiddlerSDK("ws://localhost:8000/", "test", fsm_def)


# TODO: create type out of ctx
# TODO: create type out of this return data structure and check of type on sdk handler registration
@sdk.rpc("is_saying_goodbye")
def is_saying_goodbye(ctx: dict):
    if ctx["last_mml"]["stacks"][0][0]["payload"] == "goodbye":
        return {
            "score": 1,
            "data": {}
        }
    return {
        "score": 0,
        "data": {}
    }


@sdk.rpc("say_hello")
def say_hello(ctx: dict):
    yield Text("Hello!")
    yield Text("How are you?")


@sdk.rpc("create_answer")
def create_answer(ctx: dict):
    last_payload = ctx['last_mml']['stacks'][0][0]['payload']
    yield Text(f'My answer to your message: "{last_payload}" is: {random.randint(0, 999)}')
    yield Text(f'Tell me more')


@sdk.rpc("create_goodbye_answer")
def create_goodbye_answer(ctx: dict):
    yield Text("Byeeeeeeee!")


sdk.connect()
