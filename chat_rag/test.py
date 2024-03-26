import json
import requests

# Define the arguments
messages = [{'role': 'user', 'content': "Who worked for Roda"}]
prev_contents = []
prompt_structure_dict = {
    "system_prefix": "You are a helpful assistant",
    "n_contexts_to_use": 3,
    "system_tag": "",
    "system_end": "",
    "user_tag": "",
    "user_end": "",
    "assistant_tag": "",
    "assistant_end": "",
}
generation_config_dict = {
    "temperature": 0.2,
    "top_p": 0.9,
    "top_k": 50,
    "max_new_tokens": 100,
    "repetition_penalty": 1.2,
    "seed": 42,
}

# Create the request data
request_data = {
    "messages": messages,
    "prev_contents": prev_contents,
    "prompt_structure_dict": prompt_structure_dict,
    "generation_config_dict": generation_config_dict,
}

request_data = {
    "model": "claude-3-sonnet-20240229",
    "message": "Count from 1 to 100"
}

# async def test_rag_deployment():
#     async with aiohttp.ClientSession() as session:
#         url = "http://localhost:10002/rag"
#         headers = {"Content-Type": "application/json"}
#         async with session.post(url, headers=headers, data=json.dumps(request_data)) as response:
#             if response.status == 200:
#                 async for chunk in response.content.iter_chunked(1):
#                     print(chunk.decode(), end='')
#             else:
#                 print(f"Error: {response.status} - {await response.text()}")

# asyncio.run(test_rag_deployment())

import time
import requests

data = {
    'model': 'gpt-3.5-turbo',
    'message': 'Count from 0 to 40',
}

r = requests.post("http://localhost:10002/arag", stream=True, json=data)
start = time.time()
r.raise_for_status()
for chunk in r.iter_content(chunk_size=None, decode_unicode=True):
    print(f"Got result {round(time.time()-start, 1)}s after start: '{chunk}'")

