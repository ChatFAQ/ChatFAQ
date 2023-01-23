from riddler_sdk import RiddlerSDK
from tests.fsm_def import fsm_def

sdk = RiddlerSDK("ws://localhost:8000/", "simple_fsm", fsm_def)
sdk.connect()
