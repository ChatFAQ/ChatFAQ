import os
from pathlib import Path

from chatfaq_sdk import ChatFAQSDK, FSMDefinition, DataSourceParser
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(dotenv_path=BASE_DIR / ".env")


def make_chatfaq_sdk(
    fsm_name: str,
    fsm_definition: FSMDefinition,
    overwrite_definition: bool = False,
    chatfaq_ws: str = os.getenv("CHATFAQ_BACKEND_WS"),
    chatfaq_http: str = os.getenv("CHATFAQ_BACKEND_HTTP"),
    token: str = os.getenv("CHATFAQ_TOKEN"),
    data_source_parsers: dict[str, DataSourceParser] = {},
):
    """
    This function is used to create a ChatFAQSDK instance with the given parameters

    Parameters
    ----------
    data_source_parsers
    fsm_name
    fsm_definition
    chatfaq_ws
    token

    Returns
    -------

    """
    sdk = ChatFAQSDK(
        chatfaq_ws=chatfaq_ws,
        chatfaq_http=chatfaq_http,
        token=token,
        fsm_name=fsm_name,
        fsm_definition=fsm_definition,
        overwrite_definition=overwrite_definition,
        data_source_parsers=data_source_parsers,
    )

    return sdk
