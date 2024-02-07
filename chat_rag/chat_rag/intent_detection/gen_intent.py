from typing import List

from openai import OpenAI


def generate_intents(
    intent_queries_list: List[List[str]], max_new_tokens=100
) -> List[str]:
    """
    Generate a batch of texts from a given instruction and a list of text inputs.
    Parameters
    ----------
    intent_queries_list : List[List[str]]
        List containing lists of intent queries.
    max_new_tokens : int, optional
        Maximum number of tokens to be generated, by default 100
    Returns
    -------
    List[str]
        List of generated intents.
    """
    client = OpenAI()

    instruction = "Summarize the intent that represents all the following questions in a few words:",

    # Generate prompts for each intent
    input_texts = []
    for intent_queries in intent_queries_list:
        intent_queries = list(set(intent_queries))
        input_text = f"{instruction}\n"

        # Append each query
        for query in intent_queries[:10]:
            input_text += f"- {query}\n"

        input_text += "The intent is to "
        input_texts.append(input_text)

    responses = []
    #batches of 20
    for i in range(0, len(input_texts), 20):
        result = client.completions.create(model='gpt-3.5-turbo-instruct',
        prompt=input_texts[i:i+20],
        temperature=0.5,
        max_tokens=max_new_tokens).choices
        responses.extend(result)

    return ['To ' + response.text for response in responses]