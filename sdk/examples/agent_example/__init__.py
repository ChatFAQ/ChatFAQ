from examples import make_chatfaq_sdk
from examples.agent_example.fsm_definition import fsm_definition


def main():
    sdk = make_chatfaq_sdk(
        fsm_name="agent_fsm",
        fsm_definition=fsm_definition,
    )
    sdk.connect()
