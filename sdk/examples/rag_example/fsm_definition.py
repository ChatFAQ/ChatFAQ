from chatfaq_sdk import ChatFAQSDK
from chatfaq_sdk.fsm import FSMDefinition, State, Transition
from chatfaq_sdk.layers import Message, StreamingMessage
from chatfaq_sdk.clients import llm_request, retrieve
from chatfaq_sdk.utils import convert_mml_to_llm_format
from .prompts import rag_system_prompt


async def send_greeting(sdk: ChatFAQSDK, ctx: dict):
    yield Message("How can we help you?", allow_feedback=False)


async def send_rag_answer(sdk: ChatFAQSDK, ctx: dict):

    messages = convert_mml_to_llm_format(ctx["conv_mml"][1:])
    last_user_message = messages[-1]["content"]

    # Retrieve context
    contexts = await retrieve(sdk, 'chatfaq_retriever', last_user_message, top_k=3, bot_channel_name=ctx["bot_channel_name"])

    # Augment prompt with context
    system_prompt = rag_system_prompt
    context_content = "\n".join([f"- {context['content']}" for context in contexts.get('knowledge_items', [])])
    system_prompt += f"\nInformation:\n{context_content}"
    messages.insert(0, {"role": "system", "content": system_prompt})

    # Generate response
    generator = llm_request(
        sdk,
        "gpt-4o",
        use_conversation_context=False,
        conversation_id=ctx["conversation_id"],
        bot_channel_name=ctx["bot_channel_name"],
        messages=messages,
    )

    yield StreamingMessage(generator, references=contexts)

greeting_state = State(name="Greeting", events=[send_greeting], initial=True)

answering_state = State(
    name="Answering",
    events=[send_rag_answer],
)

_to_answer = Transition(
    dest=answering_state,
)

fsm_definition = FSMDefinition(
    states=[greeting_state, answering_state],
    transitions=[_to_answer]
)
