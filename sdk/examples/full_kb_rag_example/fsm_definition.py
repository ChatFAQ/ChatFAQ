from chatfaq_sdk import ChatFAQSDK
from chatfaq_sdk.clients import llm_request, query_kis
from chatfaq_sdk.fsm import FSMDefinition, State, Transition
from chatfaq_sdk.layers import Message, StreamingMessage
from chatfaq_sdk.utils import convert_mml_to_llm_format


"""
This FSM is a simple example of how to do RAG with the whole knowledge base, given that context windows are 
growing for some uses cases we may not need to do retrieval and just pass the whole knowledge base to the LLM.
"""


async def send_greeting(sdk: ChatFAQSDK, ctx: dict):
    yield Message("How can I help you today?", allow_feedback=False)


async def send_rag_answer(sdk: ChatFAQSDK, ctx: dict):
    messages = convert_mml_to_llm_format(ctx["conv_mml"][1:])

    # Get all the knowledge items from the knowledge base
    # TODO: Replace with actual knowledge base name.
    knowledge_base = "example_kb"
    knowledge_items = await query_kis(sdk, knowledge_base)

    # Create system prompt with context
    system_prompt = """You are a helpful assistant that answers questions based on the provided information.
Your task is to answer the user's question using ONLY the information provided below.
If you cannot answer the question based on the provided information, say so."""

    # Add context from knowledge items
    if knowledge_items:
        context_content = "\n".join([f"- {item.content}" for item in knowledge_items])
        system_prompt += f"\n\nInformation:\n{context_content}"
    else:
        system_prompt += "\n\nNo relevant information found."

    # Prepare messages for LLM
    messages.insert(0, {"role": "system", "content": system_prompt})

    # Generate response
    generator = llm_request(
        sdk,
        "gpt-4o",  # TODO: Replace with your actual LLM config name
        use_conversation_context=False,
        conversation_id=ctx["conversation_id"],
        bot_channel_name=ctx["bot_channel_name"],
        messages=messages,
    )

    yield StreamingMessage(generator, references=knowledge_items)


# Define states
greeting_state = State(name="Greeting", events=[send_greeting], initial=True)
answering_state = State(name="Answering", events=[send_rag_answer])

# Define transitions
to_answer = Transition(dest=answering_state)

# Create FSM definition
fsm_definition = FSMDefinition(
    states=[greeting_state, answering_state], transitions=[to_answer]
)
