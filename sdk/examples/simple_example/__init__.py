from .fsm_definition import fsm_definition
from .. import make_chatfaq_sdk


def main():
    sdk = make_chatfaq_sdk(
        fsm_name="simple_fsm",
        fsm_definition=fsm_definition,
    )
    sdk.connect()
