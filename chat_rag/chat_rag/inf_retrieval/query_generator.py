from typing import List
import json

from openai import OpenAI


SYSTEM_PROMPT_QUESTIONS = """Please generate {} question asking for the key information in the user passage.
Please ask specifics questions instead of general questions, like
'What is the key information in the given paragraph?'.
The questions should be in the same language as the user passage.
Please call the process_questions function to submit the generated questions."""


TOOLS_QUESTIONS = [
    {
        "type": "function",
        "function": {
            "name": "submit_questions",
            "description": "Submits questions for the user passage.",
            "parameters": {
                "type": "object",
                "properties": {
                    "questions": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "An array of questions."
                    },
                },
                "required": ["questions"]
            },
        },
    }
]


SYSTEM_PROMPT_QUESTION = """Please generate a question asking for the key information in the user passage.
Please ask a specific question instead of general questions, like
'What is the key information in the given paragraph?'.
The question should be in the same language as the user passage.
Please call the process_questions function to submit the generated question."""

TOOLS_QUESTION = [
    {
        "type": "function",
        "function": {
            "name": "submit_question",
            "description": "Submits question for the user passage.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question to submit.",
                    },
                },
                "required": ["question"]
            },
        },
    }
]


models_dict = {
    'en': {
        'gpt-4': 'gpt-4-1106-preview',
        'gpt-3.5': 'gpt-3.5-turbo-1106'
    },
    'multilingual': {
        'gpt-4': 'gpt-4-0613', # the 1106 version returns bad characters https://community.openai.com/t/gpt-4-1106-preview-messes-up-function-call-parameters-encoding/478500
        # no 3.5 version before 1106 for function calls
    }
}


class QueryGenerator:
    def __init__(self, api_key, lang: str = 'en', model: str = 'gpt-4', base_url: str = None) -> None:
        """
        Class to generate questions from a given passage.
        Currently it only uses the OpenAI API.
        Parameters
        ----------
        api_key: str
            OpenAI API key.
        lang: str
            Language of the model to use.
        model: str
            Model to use.
        base_url: str
            Base url to use for the OpenAI client.
        """

        lang = lang if lang in models_dict else 'multilingual'

        assert lang in models_dict.keys(), f'No model available for {lang}'
        assert model in models_dict[lang].keys(), f'No model available for {lang} and {model}'

        self.model_name = models_dict[lang][model]
        
        if base_url is None:
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = OpenAI(base_url=base_url)

    def __call__(self, passage: str, n_queries: int = 5) -> List[str]:
        """
        Generate questions from a given passage.
        Parameters
        ----------
        passage: str
            The passage to generate questions from.
        n_queries: int
            Number of questions to generate.
        Returns
        -------
        List[str]
            List of generated questions.
        """
        

        if n_queries == 1:
            system_prompt = SYSTEM_PROMPT_QUESTION
            tools = TOOLS_QUESTION
        else:
            system_prompt = SYSTEM_PROMPT_QUESTIONS.format(n_queries)
            tools = TOOLS_QUESTIONS
            tools[0]['function']['parameters']['properties']['questions']['minItems'] = n_queries
            tools[0]['function']['parameters']['properties']['questions']['maxItems'] = n_queries

        
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': passage},
        ]

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            tools=tools,
            tool_choice='auto'
        )

        args = json.loads(response.choices[0].message.tool_calls[0].function.arguments)

        return args['questions'] if n_queries > 1 else args['question']