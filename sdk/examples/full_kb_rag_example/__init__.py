from examples import make_chatfaq_sdk
from examples.full_kb_rag_example.fsm_definition import fsm_definition


def main():
    sdk = make_chatfaq_sdk(
        fsm_name="full_kb_rag_fsm",
        fsm_definition=fsm_definition,
    )
    sdk.connect()
