import time

from chatfaq_sdk import ChatFAQSDK
from chatfaq_sdk.clients import llm_request
from chatfaq_sdk.fsm import FSMDefinition, State, Transition
from chatfaq_sdk.layers import Message, ThumbsRating
from chatfaq_sdk.utils import convert_mml_to_llm_format

# pip install presidio-analyzer presidio-anonymizer spacy faker
# python -m spacy download en_core_web_lg
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from faker import Faker

t1 = time.perf_counter()
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()
t2 = time.perf_counter()
print(f"Time taken to initialize Presidio: {t2 - t1} seconds")

fake = Faker()

# --- Presidio Setup ---
# Using simple replacement for demonstration. Configure as needed.
# You might want to use Faker or other operators for more robust anonymization.
operators = {
    "DEFAULT": OperatorConfig("replace", {"new_value": "<ANONYMIZED>"}),
    "PERSON": OperatorConfig("replace", {"new_value": fake.name()}),
    "LOCATION": OperatorConfig("replace", {"new_value": fake.city()}),
    "PHONE_NUMBER": OperatorConfig("replace", {"new_value": fake.phone_number()}),
    # Add more entities as needed
}


async def send_greeting(sdk: ChatFAQSDK, ctx: dict):
    yield Message("Hello! How can I help you today?")


async def anonymize_and_send_answer(sdk: ChatFAQSDK, ctx: dict):
    deanonymization_mapping = {}  # Reset for each turn

    # 1. Get the last user message
    user_message_mml = ctx["conv_mml"][-1]
    print(f"DEBUG: User message MML: {user_message_mml}")
    original_user_text = user_message_mml["stack"][-1]["payload"]["content"]

    # 2. Analyze user message
    t1 = time.perf_counter()
    analyzer_results = analyzer.analyze(text=original_user_text, language="en")
    t2 = time.perf_counter()
    print(f"Time taken to analyze user message: {t2 - t1} seconds")
    print(f"DEBUG: Analyzer results: {analyzer_results}")

    # 3. Anonymize user message
    t1 = time.perf_counter()
    anonymizer_result = anonymizer.anonymize(
        text=original_user_text, analyzer_results=analyzer_results, operators=operators
    )
    t2 = time.perf_counter()
    print(f"Time taken to anonymize user message: {t2 - t1} seconds")
    anonymized_user_text = anonymizer_result.text
    print(f"DEBUG: Anonymized user text: {anonymized_user_text}")
    # 4. Store deanonymization mapping
    # Reconstruct mapping from analyzer results and anonymizer output
    temp_mapping = {}
    for result in sorted(analyzer_results, key=lambda x: x.start):
        # Find the *actual* placeholder used by the specific operator config
        entity_type = result.entity_type
        if entity_type in operators:
            placeholder = operators[entity_type].params.get(
                "new_value", operators["DEFAULT"].params["new_value"]
            )
        else:
            placeholder = operators["DEFAULT"].params["new_value"]

        original_value = original_user_text[result.start : result.end]
        if placeholder not in temp_mapping:
            temp_mapping[placeholder] = original_value

    deanonymization_mapping = temp_mapping
    print(f"DEBUG: Deanonymization Mapping: {deanonymization_mapping}")

    # 5. Prepare messages for LLM
    messages = convert_mml_to_llm_format(ctx["conv_mml"][1:])  # skip the greeting
    messages.insert(
        0,
        {
            "role": "system",
            "content": "You are a helpful assistant. Respond naturally, even if the user's message contains placeholders like <PERSON> or <LOCATION>.",
        },
    )
    # Ensure the last message content (user's) is the anonymized version if anonymization occurred
    messages[-1]["content"] = anonymized_user_text

    print(f"DEBUG: Messages: {messages}")

    # 6. Call LLM
    response = await llm_request(
        sdk,
        "gpt-4o",  # Replace with your desired model
        use_conversation_context=False,  # We are managing context manually here
        conversation_id=ctx["conversation_id"],
        bot_channel_name=ctx["bot_channel_name"],
        messages=messages,
        stream=False,  # Set to True for streaming if needed
    )

    llm_response_text = response["content"][0]["text"]
    print(f"DEBUG: Raw LLM Response: {llm_response_text}")

    # 7. Deanonymize LLM response
    deanonymized_response_text = llm_response_text
    # Replace placeholders based on the stored mapping
    for placeholder, original_value in deanonymization_mapping.items():
        # Simple replacement. Might need refinement for edge cases.
        deanonymized_response_text = deanonymized_response_text.replace(
            placeholder, original_value
        )

    print(f"DEBUG: Deanonymized Response: {deanonymized_response_text}")

    # 8. Yield final response and follow-ups
    yield Message(deanonymized_response_text)
    yield ThumbsRating()


# --- FSM Definition ---
greeting_state = State(name="Greeting", events=[send_greeting], initial=True)

answering_state = State(
    name="Answering",
    events=[anonymize_and_send_answer],
)

# Transition from Greeting to Answering on any user message
_to_answer = Transition(
    dest=answering_state,
    # Add conditions if needed, e.g., only transition on user input
    # conditions=[lambda ctx: ctx.get("last_event_type") == "user_message"]
)

# You might need a transition back to Answering for multi-turn conversations
_stay_answering = Transition(
    source=answering_state,
    dest=answering_state,
)


fsm_definition = FSMDefinition(
    states=[greeting_state, answering_state],
    transitions=[_to_answer, _stay_answering],  # Add transitions as needed
)
