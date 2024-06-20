import asyncio
import json
from typing import Dict, List

from pydantic import BaseModel, Field

from chat_rag.llms import LLM


class SubmitClusterTitle(BaseModel):
    title: str = Field(
        ...,
        title="Cluster Title",
        description="The title you would assign to the cluster of knowledge items.",
    )


USER_MESSAGE = """You will be assigning representative names/titles to clusters of "knowledge items". Knowledge items are chunks of content extracted from documents like PDFs, Word files, web pages, etc. Each knowledge item has a title and content. 

Here is the full set of knowledge items of a cluster:

{items}

Your task is to assign a clear name/title to each cluster that captures the main theme, topic, or intent that the knowledge items in that cluster have in common.

Look for commonalities across the items to identify the central theme, topic, or intent that links them together. 

The names should be clear, specific, and representative of the cluster's contents. Avoid vague or overly broad names.

The cluster title should be in the same language as the knowledge items.
"""


def generate_intent(cluster_texts: List[Dict], llm: LLM) -> str:
    """
    Generates an intent for the given cluster texts.
    Parameters
    ----------
    cluster_texts : List[Dict]
        List of dictionaries containing the cluster title and items.
    llm : LLM
        The language model to use.
    Returns
    -------
    str
        The generated intents.
    """
    # Pick five items of the cluster. We should have a better way to handle this for not exceeding the llm context length.
    items = json.dumps(cluster_texts[:5])

    messages = [{"role": "user", "content": USER_MESSAGE.format(items=items)}]

    # structured generation
    response = llm.generate(
        messages, tools=[SubmitClusterTitle], tool_choice="SubmitClusterTitle"
    )

    return json.loads(response[0]["args"])["title"]


async def agenerate_intent(cluster_texts: List[Dict], llm: LLM) -> str:
    """
    Generates an intent for the given cluster texts.
    Parameters
    ----------
    cluster_texts : List[Dict]
        List of dictionaries containing the cluster title and items.
    llm : LLM
        The language model to use.
    Returns
    -------
    str
        The generated intents.
    """
    items = json.dumps(cluster_texts[:5])
    messages = [{"role": "user", "content": USER_MESSAGE.format(items=items)}]
    response = await llm.agenerate(
        messages, tools=[SubmitClusterTitle], tool_choice="SubmitClusterTitle"
    )
    return json.loads(response[0]["args"])["title"]


# Batch processing
async def agenerate_intents(clusters_texts: List[List[Dict]], llm: LLM) -> List[str]:
    """
    Generate intents for the given clusters texts.
    Parameters
    ----------
    clusters_texts : List[List[Dict]]
        List of list of dictionaries containing the cluster texts.
    llm : LLM
        The language model to use.
    Returns
    -------
    List[str]
        The generated intents.
    """
    tasks = [agenerate_intent(cluster_texts, llm) for cluster_texts in list(clusters_texts.values())]
    intents =  await asyncio.gather(*tasks)
    return intents
