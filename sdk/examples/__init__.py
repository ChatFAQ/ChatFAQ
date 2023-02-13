from examples.fsm_def import fsm_def
from chatfaq_sdk import ChatFAQSDK
from dotenv import load_dotenv
import os

load_dotenv()

sdk = ChatFAQSDK(
    os.getenv('CHATFAQ_BACKEND_WS'),
    os.getenv('CHATFAQ_BACKEND_EMAIL'),
    os.getenv('CHATFAQ_BACKEND_PASSWORD'),
    "simple_fsm",
    fsm_def
)

sdk.connect()
