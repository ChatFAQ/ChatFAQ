from chatfaq_sdk import ChatFAQSDK
from chatfaq_sdk.fsm import FSMDefinition, State, Transition
from chatfaq_sdk.layers import Text
from chatfaq_sdk.clients import llm_request
from .prompts import travel_place_q


PLACES = ["Madrid", "Paris", "Rome"]


async def send_greeting(sdk: ChatFAQSDK, ctx: dict):
    yield Text(
        "Hi, let’s find a great destination for your next trip", allow_feedback=False
    )

    # Very expensive to generate this each time a conversation is started, we should cache this
    # and regenerate it only when the list of places changes
    response = ""
    generator = llm_request(
        sdk,
        "gpt-4o",
        use_conversation_context=False,
        conversation_id=ctx["conversation_id"],
        bot_channel_name=ctx["bot_channel_name"],
        messages=[
            {
                "role": "user",
                "content": travel_place_q.format(PLACES_LIST=", ".join(PLACES)),
            }
        ],
    )
    async for chunk in generator:
        response += chunk["model_response"]

    response = response.split("<question>")[1].split("</question>")[0].strip()
    print(response)
    yield Text(response, allow_feedback=False)

    yield Text("To continue, please provide a description of your ideal travel experience", allow_feedback=False)



greeting_state = State(name="Greeting", events=[send_greeting], initial=True)


fsm_definition = FSMDefinition(
    states=[greeting_state]
)
