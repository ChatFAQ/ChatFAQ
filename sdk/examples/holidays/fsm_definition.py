from chatfaq_sdk import ChatFAQSDK
from chatfaq_sdk.fsm import FSMDefinition, State, Transition
from chatfaq_sdk.layers import Message
from chatfaq_sdk.clients import llm_request
from .prompts import travel_place_q, collect_place_p, collect_budget_p


DEFAULT_PLACES = ["Madrid", "Paris", "Rome"]



def submit_budget(budget: str):
    """
    Submit the user's budget for their planned holiday.
    :param budget: The user's budget for their planned holiday.
    :return: The user's budget for their planned holiday.
    """
    return {"budget": budget}


def submit_place(place: str):
    """
    Submit the user's place for their planned holiday.
    :param place: The user's place for their planned holiday.
    :return: The user's place for their planned holiday.
    """
    return {"place": place}


async def send_places(sdk: ChatFAQSDK, ctx: dict):
    # yield Message(
    #     "Hi, let’s find a great destination for your next trip"
    # )

    state = ctx["state"] if ctx["state"] else {}
    places = state["places"] if "places" in state else DEFAULT_PLACES

    # Very expensive to generate this each time a conversation is started, we should cache this
    # and regenerate it only when the list of places changes
    response = ""
    response = await llm_request(
        sdk,
        "gpt-4o",
        use_conversation_context=False,
        conversation_id=ctx["conversation_id"],
        bot_channel_name=ctx["bot_channel_name"],
        messages=[
            {
                "role": "user",
                "content": travel_place_q.format(PLACES_LIST=", ".join(places)),
            }
        ],
    )
    response = response['content'][0]['text']

    response = response.split("<question>")[1].split("</question>")[0].strip()
    yield Message(response)

    # yield Message("To continue, please provide a description of your ideal travel experience")


async def collect_place(sdk: ChatFAQSDK, ctx: dict):
    places = ctx["state"]["places"] if "places" in ctx["state"] else DEFAULT_PLACES

    response = await llm_request(
        sdk,
        "gpt-4o",
        use_conversation_context=True, # Here we let the backend append all the previous messages to send to the LLM
        conversation_id=ctx["conversation_id"],
        bot_channel_name=ctx["bot_channel_name"],
        tools=[submit_place],
        tool_choice="submit_place",
        messages=[
            {
                "role": "system",
                "content": collect_place_p.format(PLACES=", ".join(places)),
            }
        ],
    )

    place = None
    for part in response['content']:
        if part['type'] == 'tool_use':
            place = part['tool_use']['args']['place']
            break

    # Start the state and submit it so other states can access it
    state = {"place": place}

    yield Message(f"Great! Then {place} is the best destination. What budget are you willing to go?", state=state)


async def collect_budget(sdk: ChatFAQSDK, ctx: dict):
    user_budget = ctx["conv_mml"][-1]["stack"][0]["payload"]["content"]
    state = ctx["state"]

    response = await llm_request(
        sdk,
        "gpt-4o",
        use_conversation_context=False, # Here we control exactly which messages are sent to the LLM
        conversation_id=ctx["conversation_id"],
        bot_channel_name=ctx["bot_channel_name"],
        tools=[submit_budget],
        tool_choice="submit_budget",
        messages=[
            {
                "role": "user",
                "content": collect_budget_p.format(USER_INPUT=user_budget),
            }
        ],
    )

    budget = None
    for part in response['content']:
        if part['type'] == 'tool_use':
            budget = part['tool_use']['args']['budget']
            break

    state["budget"] = budget

    yield Message(f"Great. Let me find vacations in {state['place']} with budget {budget}", state=state)


places_options_state = State(name="Greeting", events=[send_places], initial=True)

collect_place_state = State(name="CollectPlace", events=[collect_place])

collect_budget_state = State(name="CollectBudget", events=[collect_budget])

_to_collect_place = Transition(
    source=places_options_state,
    dest=collect_place_state,
)

_to_collect_budget = Transition(
    source=collect_place_state,
    dest=collect_budget_state,
)

fsm_definition = FSMDefinition(
    states=[places_options_state, collect_place_state, collect_budget_state], transitions=[_to_collect_place, _to_collect_budget]
)
