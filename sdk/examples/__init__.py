from examples.fsm_def import fsm_def
from riddler_sdk import RiddlerSDK
from dotenv import load_dotenv
import os

load_dotenv()

sdk = RiddlerSDK(
    os.getenv('RIDDLER_WS'),
    os.getenv('RIDDLER_EMAIL'),
    os.getenv('RIDDLER_PASSWORD'),
    "simple_fsm",
    fsm_def
)

sdk.connect()
