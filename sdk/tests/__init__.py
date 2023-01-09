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


sdk.connect()
