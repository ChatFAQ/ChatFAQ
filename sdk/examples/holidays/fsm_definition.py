from chatfaq_sdk import ChatFAQSDK
from chatfaq_sdk.fsm import FSMDefinition, State, Transition
from chatfaq_sdk.layers import Text
from chatfaq_sdk.clients import llm_request
from .prompts import travel_place_q, collect_place_p, collect_budget_p
from pydantic import BaseModel, Field
from typing import Literal
import json


PLACES = ["Madrid", "Paris", "Rome"]

class SubmitPlace(BaseModel):
    place: Literal["Madrid", "Paris", "Rome"] = Field(
        ...,
        title="Place",
        description="The place that most closely matches the description."
    )

class SubmitBudget(BaseModel):
    budget: str = Field(
        ...,
        title="Budget",
        description="The user's budget for their planned holiday."
    )


async def send_places(sdk: ChatFAQSDK, ctx: dict):
    # yield Text(
    #     "Hi, let’s find a great destination for your next trip", allow_feedback=False
    # )

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

    # yield Text("To continue, please provide a description of your ideal travel experience", allow_feedback=False)


async def collect_place(sdk: ChatFAQSDK, ctx: dict):
    user_description = ctx["last_mml"]["stack"][0]["payload"]

    generator = llm_request(
        sdk,
        "gpt-4o",
        use_conversation_context=False,
        conversation_id=ctx["conversation_id"],
        bot_channel_name=ctx["bot_channel_name"],
        tools=[SubmitPlace],
        tool_choice="SubmitPlace",
        messages=[
            {
                "role": "user",
                "content": collect_place_p.format(PLACES=", ".join(PLACES), USER_DESCRIPTION=user_description),
            }
        ],
    )

    place = None
    async for place in generator:
        print(place)
        args = place['tool_use'][0]['args']
        args = json.loads(args)
        place = args['place']
    
    # Start the state and submit it so other states can access it
    state = {"place": place}

    yield Text(f"Great! Then {place} is the best destination. What budget are you willing to go?", allow_feedback=False, state={"place": final_place})


async def collect_budget(sdk: ChatFAQSDK, ctx: dict):
    user_budget = ctx["last_mml"]["stack"][0]["payload"]
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
                "role": "user",
                "content": collect_budget_p.format(USER_INPUT=user_budget),
            }
        ],
    )

    budget = None
    async for budget in generator:
        print(budget)
        args = budget['tool_use'][0]['args']
        args = json.loads(args)
        budget = args['budget']
    
    state["budget"] = budget
        
    yield Text(f"Great. Let me find vacations in {state['place']} with budget {budget}", allow_feedback=False, state=state)
    

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
