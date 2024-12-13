from chatfaq_sdk import ChatFAQSDK
from chatfaq_sdk.fsm import FSMDefinition, State, Transition
from chatfaq_sdk.layers import Message, FileDownload, FileUpload


async def send_greeting(sdk: ChatFAQSDK, ctx: dict):
    yield FileUpload(content="Please upload a file", file_extensions=["pdf", "xml"], max_size=50*1024*1024)


async def send_answer(sdk: ChatFAQSDK, ctx: dict):
    # Last message
    file_name = ctx['conv_mml'][-1]['stack'][0]['payload']['name']
    file_url = ctx['conv_mml'][-1]['stack'][0]['payload']['url']
    print("file_name: ", file_name)
    print("file_url: ", file_url)

    ########################################
    # Do some processing with the file here
    new_file_name = "processed_" + file_name
    new_file_url = file_url
    ########################################

    yield Message(content="Here is the processed file")
    yield FileDownload(file_url=new_file_url, file_name=new_file_name)



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
