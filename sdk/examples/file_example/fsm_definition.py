from chatfaq_sdk import ChatFAQSDK
from chatfaq_sdk.fsm import FSMDefinition, State, Transition
from chatfaq_sdk.layers import FileDownload, FileUpload, Message


async def send_greeting(sdk: ChatFAQSDK, ctx: dict):
    yield FileUpload(
        content="Please upload up to 5 files (PDF or XML)", 
        file_extensions=["pdf", "xml"], 
        max_size=50*1024*1024,
        max_files=5
    )


async def send_answer(sdk: ChatFAQSDK, ctx: dict):
    # Last message payload
    payload = ctx['conv_mml'][-1]['stack'][0]['payload']
    processed_files = []
    
    # Handle new multiple files format
    if 'files' in payload:
        print("Processing multiple files:")
        for file_data in payload['files']:
            file_name = file_data['name']
            file_url = file_data['url']
            print(f"- file_name: {file_name}")
            print(f"- file_url: {file_url}")
            
            ########################################
            # Do some processing with each file here
            new_file_name = "processed_" + file_name
            new_file_url = file_url  # In reality, you'd process and upload to new location
            ########################################
            
            processed_files.append({
                "name": new_file_name,
                "url": new_file_url
            })
    else:
        print("No files found in payload")
        yield Message(content="No files were uploaded to process.")
        return

    # Send back the processed files
    yield FileDownload(
        content=f"Here {'are' if len(processed_files) > 1 else 'is'} the processed file{'s' if len(processed_files) > 1 else ''}:",
        files=processed_files
    )


greeting_state = State(name="Greeting", events=[send_greeting], initial=True)

answering_state = State(
    name="Answering",
    events=[send_answer],
)

_to_answer = Transition(
    dest=answering_state,
)

fsm_definition = FSMDefinition(
    states=[greeting_state, answering_state],
    transitions=[_to_answer]
)
