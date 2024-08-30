from chatfaq_sdk import ChatFAQSDK
from chatfaq_sdk.fsm import FSMDefinition, State, Transition
from chatfaq_sdk.layers import Text
from chatfaq_sdk.clients import llm_request
from chatfaq_sdk.conditions import Condition
from .prompts import travel_place_q, collect_place_p, collect_budget_p, confirm_search
from .prompts import confirm_default_place, confirm_selected_place
from .places import place_catalog, recommended_place
from pydantic import BaseModel, Field
import json


class SubmitBudget(BaseModel):
    budget: str = Field(
        ...,
        title="Budget",
        description="The user's budget for their planned holiday."
    )


async def send_places(sdk: ChatFAQSDK, ctx: dict):
    # yield Text(
    #     f"Bonjour, où veux-tu partir pour tes prochaines vacances ?", allow_feedback=False
    # )

    state = ctx["state"] if ctx["state"] else {}
    places = state["places"] if "places" in state else place_catalog

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
                "content": travel_place_q.format(PLACES_LIST=", ".join(places)),
            }
        ],
    )
    async for chunk in generator:
        response += chunk["model_response"]

    response = response.split("<question>")[1].split("</question>")[0].strip()
    yield Text(response, allow_feedback=False)


async def collect_place(sdk: ChatFAQSDK, ctx: dict):
    places = ctx["state"]["places"] if "places" in ctx["state"] else place_catalog
    user_response = ctx["conv_mml"][-1]["stack"][0]["payload"]

    class SubmitPlace(BaseModel):
        place: str = Field(
            ...,
            title="Place",
            description=f"The place that most closely matches the description between {', '.join(places)}",
        )

    generator = llm_request(
        sdk,
        "gpt-4o",
        use_conversation_context=True,
        conversation_id=ctx["conversation_id"],
        bot_channel_name=ctx["bot_channel_name"],
        tools=[SubmitPlace],
        tool_choice="SubmitPlace",
        messages=[
            {
                "role": "system",
                "content": collect_place_p.format(PLACES=", ".join(places)),
            },
            {
                "role": "user",
                "content": user_response,
            },
        ],
    )

    place = None
    async for place in generator:
        args = place['tool_use'][0]['args']
        args = json.loads(args)
        place = args['place']

    print("Place: ", place)

    if place == "whatever":
        # If we couldn't determine the place from the user response, we make our recommendation
        prompt = confirm_default_place.format(user_response=user_response, default_place=recommended_place)
    else:
        # We confirm his choice
        prompt = confirm_selected_place.format(user_response=user_response, place=place)

    clarification_generator = llm_request(
        sdk,
        "gpt-4o",
        use_conversation_context=True,
        conversation_id=ctx["conversation_id"],
        bot_channel_name=ctx["bot_channel_name"],
        messages=[
            {
                "role": "system",
                "content": prompt
            }
        ],
    )

    clarification_response = ""
    async for chunk in clarification_generator:
        clarification_response += chunk["model_response"]

    yield Text(clarification_response, allow_feedback=False, state={"place": place})


async def collect_budget(sdk: ChatFAQSDK, ctx: dict):
    user_budget = ctx["conv_mml"][-1]["stack"][0]["payload"]
    state = ctx["state"]

    generator = llm_request(
        sdk,
        "gpt-4o",
        use_conversation_context=False,
        conversation_id=ctx["conversation_id"],
        bot_channel_name=ctx["bot_channel_name"],
        tools=[SubmitBudget],
        tool_choice="SubmitBudget",
        messages=[
            {
                "role": "system",
                "content": collect_budget_p.format(USER_INPUT=user_budget),
            }
        ],
    )

    budget = None
    async for budget in generator:
        args = budget['tool_use'][0]['args']
        args = json.loads(args)
        budget = args['budget']

    state["budget"] = budget
    place = state['place']
    budget_collect_generator = llm_request(
        sdk,
        "gpt-4o",
        use_conversation_context=False,
        conversation_id=ctx["conversation_id"],
        bot_channel_name=ctx["bot_channel_name"],
        messages=[
            {
                "role": "system",
                "content": confirm_search.format(place=place, budget=budget),
            }
        ],
    )

    confirmation_response = ""
    async for chunk in budget_collect_generator:
        confirmation_response += chunk["model_response"]

    confirmation_response += "..."
    yield Text(confirmation_response, allow_feedback=False, state={"place": place, "budget": budget})


greeting_state = State(name="Greeting", events=[send_places], initial=True)

collect_place_state = State(name="CollectPlace", events=[collect_place])

collect_budget_state = State(name="CollectBudget", events=[collect_budget])

_to_collect_place = Transition(
    source=greeting_state,
    dest=collect_place_state,
)

_to_collect_budget = Transition(
    source=collect_place_state,
    dest=collect_budget_state,
)

fsm_definition = FSMDefinition(
    states=[greeting_state, collect_place_state, collect_budget_state],
    transitions=[_to_collect_place, _to_collect_budget]
)
