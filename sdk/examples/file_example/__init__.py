from examples import make_chatfaq_sdk
from examples.file_example.fsm_definition import fsm_definition


def main():
    sdk = make_chatfaq_sdk(
        fsm_name="file_fsm",
        fsm_definition=fsm_definition,
    )
    sdk.connect()
