from chatfaq_sdk.fsm import FSMDefinition, State, Transition
from chatfaq_sdk.layers import Text, StructuredGeneration
from pydantic import BaseModel

import logging

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


# Define your desired output structure
class UserInfo(BaseModel):
    name: str
    age: int


def send_greeting(ctx: dict):
    yield Text(
        "I will extract the name and age of an user description, please input the description",
        allow_feedback=False,
    )


def extract_info(ctx: dict):
    logger.info("Extracting user info...")
    yield StructuredGeneration(
        "gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are an assistant that extracts the user information from a description.",
            },
        ],
        tools=[UserInfo],
        tool_choice="UserInfo",
    )


def send_info(ctx: dict):
    print('The last MML is:')
    print(ctx["last_mml"])
    yield Text("Here is the extracted information", allow_feedback=False)



greeting_state = State(name="Greeting", events=[send_greeting], initial=True)

extract_info_state = State(
    name="Extracting Info",
    events=[extract_info],
)

send_info_state = State(
    name="Send Info",
    events=[send_info],
)

# After the initial state, always transition to the extraction state
_to_extraction = Transition(
    dest=extract_info_state,
)

_to_send_info = Transition(
    source=extract_info_state,
    dest=send_info_state,
    cascade=True,
)


fsm_definition = FSMDefinition(
    states=[greeting_state, extract_info_state, send_info_state], transitions=[_to_extraction, _to_send_info]
)

