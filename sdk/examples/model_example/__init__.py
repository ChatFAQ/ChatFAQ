from examples.model_example.fsm_definition import fsm_definition
from examples import make_chatfaq_sdk


def main():
    sdk = make_chatfaq_sdk(
        fsm_name="model_fsm",
        fsm_definition=fsm_definition,
    )
    sdk.connect()
