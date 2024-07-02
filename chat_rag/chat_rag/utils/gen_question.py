import asyncio
import json
from typing import List

from pydantic import BaseModel, Field

from chat_rag.llms import LLM


class SubmitQuestion(BaseModel):
    """Submits a question given a passage."""

    question: str = Field(..., description="The question to submit.")


USER_MESSAGE = """Please generate a question asking for the key information in the passage.
Please ask specifics questions instead of general questions, like
'What is the key information in the given paragraph?'.
The questions should be in the same language as the passage. Here is the passage:

<passage>{}</passage>"""


def generate_question(passage: str, llm: LLM) -> str:
    """Generates a question for the given passage."""
    messages = [{"role": "user", "content": USER_MESSAGE.format(passage)}]

    response = llm.generate(
        messages, tools=[SubmitQuestion], tool_choice="SubmitQuestion"
    )

    return json.loads(response[0]["args"])["question"]


async def agenerate_question(passage: str, llm: LLM) -> str:
    """Generates a question for the given passage."""
    messages = [{"role": "user", "content": USER_MESSAGE.format(passage)}]

    response = await llm.agenerate(
        messages, tools=[SubmitQuestion], tool_choice="SubmitQuestion"
    )

    return json.loads(response[0]["args"])["question"]


# Batch processing
async def agenerate_questions(passages: List[str], llm: LLM) -> List[str]:
    """
    Generate questions for the given passages.
    """
    tasks = [agenerate_question(passage, llm) for passage in passages]
    questions = await asyncio.gather(*tasks)
    return questions
