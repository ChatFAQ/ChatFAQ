from examples import make_chatfaq_sdk
from examples.holidays.fsm_definition import fsm_definition


def main():
    sdk = make_chatfaq_sdk(
        fsm_name="holidays_fsm",
        fsm_definition=fsm_definition,
    )
    sdk.connect()
