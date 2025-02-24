from chatfaq_sdk import ChatFAQSDK
from chatfaq_sdk.clients.agent import Agent
from chatfaq_sdk.fsm import FSMDefinition, State, Transition
from chatfaq_sdk.layers import Message

MODEL_NAME = "gemini-2.0-flash"

def get_weather(location: str) -> str:
    """
    Get current temperature for a given location.
    :param location: City and country e.g. Bogotá, Colombia
    :return: Current temperature for the given location
    """
    return f"The temperature in {location} is 20°C"


async def send_greeting(sdk: ChatFAQSDK, ctx: dict):
    yield Message("How can we help you?")


async def send_answer(sdk: ChatFAQSDK, ctx: dict):
    agent = Agent(
        sdk=sdk,
        model_name=MODEL_NAME,
        tools=[get_weather],
        system_instruction="You are a knowledgeable weather assistant. Use provided tools when necessary."
    )
    async for item in agent.run(ctx):
        yield item


greeting_state = State(name="Greeting", events=[send_greeting], initial=True)
answering_state = State(name="Answering", events=[send_answer])

_to_answer = Transition(dest=answering_state)

fsm_definition = FSMDefinition(
    states=[greeting_state, answering_state],
    transitions=[_to_answer]
)