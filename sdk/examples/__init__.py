from chatfaq_sdk import ChatFAQSDK, FSMDefinition
from dotenv import load_dotenv

from pathlib import Path

import os


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(dotenv_path=BASE_DIR / ".env")


def make_chatfaq_sdk(
    fsm_name: str,
    fsm_definition: FSMDefinition,
    chatfaq_ws: str = os.getenv('CHATFAQ_BACKEND_WS'),
    user_email: str = os.getenv('CHATFAQ_BACKEND_EMAIL'),
    user_password: str = os.getenv('CHATFAQ_BACKEND_PASSWORD'),
):
    """
    :param chatfaq_ws:
    :param user_email:
    :param user_password:
    :param fsm_name:
    :param fsm_definition:
    :return:
    """

    sdk = ChatFAQSDK(
        chatfaq_ws=chatfaq_ws,
        user_email=user_email,
        user_password=user_password,
        fsm_name=fsm_name,
        fsm_definition=fsm_definition,
    )

    return sdk
