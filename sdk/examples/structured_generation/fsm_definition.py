from chatfaq_sdk import ChatFAQSDK
from chatfaq_sdk.clients import llm_request
from chatfaq_sdk.fsm import FSMDefinition, State, Transition
from chatfaq_sdk.layers import Text
from pydantic import BaseModel
import json
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


async def send_greeting(sdk: ChatFAQSDK, ctx: dict):
    yield Text(
        "I will extract the name and age of an user description, please input the description",
        allow_feedback=False,
    )


async def send_info(sdk: ChatFAQSDK, ctx: dict):
    print('The last MML is:')
    print(ctx["last_mml"])
    logger.info("Extracting user info...")
    async for res in llm_request(
        sdk,
        "gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are an assistant that extracts the user information from a description.",
            },
        ],
        tools=[UserInfo],
        tool_choice="UserInfo",
        conversation_id=ctx["conversation_id"],
        bot_channel_name=ctx["bot_channel_name"],
    ):
        yield Text(f"Here is the extracted information: {json.dumps(res)}", allow_feedback=False)

greeting_state = State(name="Greeting", events=[send_greeting], initial=True)

send_info_state = State(
    name="Send Info",
    events=[send_info],
)

# After the initial state, always transition to the extraction state
_to_send_info = Transition(
    dest=send_info_state,
)


fsm_definition = FSMDefinition(
    states=[greeting_state, send_info_state], transitions=[_to_send_info]
)

