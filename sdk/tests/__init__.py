import random
from riddler_sdk import RiddlerSDK

sdk = RiddlerSDK("ws://localhost:8000/", 1)


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
    return [[{"type": "text", "payload": "Hello!"}]]


@sdk.rpc("create_answer")
def create_answer(ctx: dict):
    last_payload = ctx['last_mml']['stacks'][0][0]['payload']
    return [[{
        "type": "text",
        "payload": f'My answer to your message "{last_payload}" is: {random.randint(0, 999)}'
    }]]


@sdk.rpc("create_goodbye_answer")
def create_goodbye_answer(ctx: dict):
    return [[{"type": "text", "payload": "Byeeeeeeee!"}]]



sdk.connect()
