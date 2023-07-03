from typing import List


CONTEXT_PREFIX = {
    'en': 'Context: ',
    'fr': 'Contexte: ',
    'es': 'Contexto: ',
}

QUESTION_PREFIX = {
    'en': 'Question: ',
    'fr': 'Question: ',
    'es': 'Pregunta: ',
}


def format_prompt(query: str, contexts: List[str], system_prefix: str, system_tag: str, user_tag: str, assistant_tag: str, role_end: str, n_contexts_to_use: int = 3, lang: str = 'en') -> str:
    """
    Formats the prompt to be used by the model.
    Parameters
    ----------
    query : str
        The query to answer.
    contexts : list
        The context to use.
    system_prefix : str
        The prefix to indicate instructions for the LLM.
    system_tag : str
        The tag to indicate the start of the system prefix for the LLM.
    user_tag : str
        The tag to indicate the start of the user input.
    assistant_tag : str
        The tag to indicate the start of the assistant output.
    role_end : str
        The tag to indicate the end of the role (system role, user role, assistant role).
    n_contexts_to_use : int, optional
        The number of contexts to use, by default 3
    lang : str, optional
        The language of the prompt, by default 'en'
    """
    contexts_prompt = CONTEXT_PREFIX[lang]
    for context in contexts[:n_contexts_to_use]:
        contexts_prompt += f"{context}\n"

    if system_tag == '' or system_tag is None: # To avoid adding the role_end tag if there is no system prefix
        prompt = f"{user_tag}{contexts_prompt}{QUESTION_PREFIX[lang]}{query}{role_end}{assistant_tag}"
    else:
        prompt = f"{system_tag}{system_prefix}{role_end}{user_tag}{contexts_prompt}{QUESTION_PREFIX[lang]}{query}{role_end}{assistant_tag}"

    return prompt

