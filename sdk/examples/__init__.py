import os
from pathlib import Path

from chatfaq_sdk import ChatFAQSDK, FSMDefinition
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(dotenv_path=BASE_DIR / ".env")


def make_chatfaq_sdk(
    fsm_name: str,
    fsm_definition: FSMDefinition,
    chatfaq_ws: str = os.getenv("CHATFAQ_BACKEND_WS"),
    token: str = os.getenv("CHATFAQ_TOKEN"),
):
    """
    This function is used to create a ChatFAQSDK instance with the given parameters

    Parameters
    ----------
    fsm_name
    fsm_definition
    chatfaq_ws
    token

    Returns
    -------

    """

    sdk = ChatFAQSDK(
        chatfaq_ws=chatfaq_ws,
        token=token,
        fsm_name=fsm_name,
        fsm_definition=fsm_definition,
    )

    return sdk
