from examples import make_chatfaq_sdk
from examples.retrieve_example.fsm_definition import fsm_definition


def main():
    sdk = make_chatfaq_sdk(
        fsm_name="retriever_example",
        fsm_definition=fsm_definition,
    )
    sdk.connect()
