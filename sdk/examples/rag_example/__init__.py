from examples import make_chatfaq_sdk
from examples.rag_example.fsm_definition import fsm_definition


def main():
    sdk = make_chatfaq_sdk(
        fsm_name="rag_fsm",
        fsm_definition=fsm_definition,
        overwrite_definition=True,
    )
    sdk.connect()
