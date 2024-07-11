from examples import make_chatfaq_sdk
from examples.structured_generation.fsm_definition import fsm_definition


def main():
    sdk = make_chatfaq_sdk(
        fsm_name="model_fsm",
        fsm_definition=fsm_definition,
    )
    sdk.connect()
