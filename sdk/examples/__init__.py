from examples.fsm_def import fsm_def
from riddler_sdk import RiddlerSDK

sdk = RiddlerSDK("ws://localhost:8000/", "simple_fsm", fsm_def)
sdk.connect()
