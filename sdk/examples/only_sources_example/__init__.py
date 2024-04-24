from examples import make_chatfaq_sdk
from examples.only_sources_example.fsm_definition import fsm_definition


def main():
    sdk = make_chatfaq_sdk(
        fsm_name="only_sources_example",
        fsm_definition=fsm_definition,
    )
    sdk.connect()
