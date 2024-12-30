from examples import make_chatfaq_sdk
from examples.feedbacks_example.fsm_definition import fsm_definition


def main():
    sdk = make_chatfaq_sdk(
        fsm_name="feedbacks_fsm",
        fsm_definition=fsm_definition,
        authentication_required=False,
    )
    sdk.connect()
