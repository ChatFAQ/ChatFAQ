# This file contains code adapted from the instructor package given that the package is incompatible with the version of rich that is required by ChatFAQ current environment.
# Original author: Jason Liu
# Source: https://github.com/jxnl/instructor
# License: MIT (https://github.com/jxnl/instructor/blob/main/LICENSE)

import enum
from typing import Any, Dict, List

from docstring_parser import parse
from pydantic import BaseModel


class Mode(enum.Enum):
    """The mode to use for patching the client"""

    TOOLS = "tool_call"
    MISTRAL_TOOLS = "mistral_tools"
    ANTHROPIC_TOOLS = "anthropic_tools"


def openai_schema(model: BaseModel) -> Dict[str, Any]:
    """
    Return the schema in the format of OpenAI's schema as jsonschema

    Note:
        Its important to add a docstring to describe how to best use this class, it will be included in the description attribute and be part of the prompt.

    Returns:
        model_json_schema (dict): A dictionary in the format of OpenAI's schema as jsonschema
    """
    schema = model.model_json_schema()
    docstring = parse(model.__doc__ or "")
    parameters = {k: v for k, v in schema.items() if k not in ("title", "description")}
    for param in docstring.params:
        if (name := param.arg_name) in parameters["properties"] and (
            description := param.description
        ):
            if "description" not in parameters["properties"][name]:
                parameters["properties"][name]["description"] = description

    parameters["required"] = sorted(
        k for k, v in parameters["properties"].items() if "default" not in v
    )

    if "description" not in schema:
        if docstring.short_description:
            schema["description"] = docstring.short_description
        else:
            schema["description"] = (
                f"Correctly extracted `{model.__name__}` with all "
                f"the required parameters with correct types"
            )

    return {
        "name": schema["title"],
        "description": schema["description"],
        "parameters": parameters,
    }


def anthropic_schema(model: BaseModel) -> Dict[str, Any]:
    """
    Return the schema in the format of Anthropic's schema
    """
    schema = openai_schema(model)
    return {
        "name": schema["name"],
        "description": schema["description"],
        "input_schema": model.model_json_schema(),
    }


def format_tools(tools: List[BaseModel], mode: Mode) -> List[Dict[str, Any]]:
    """
    Given a series of Pydantic models, return the JSON schema required by each LLM provider.
    Parameters
    ----------
    tools : List[BaseModel]
        A list of Pydantic models
    mode : Mode
        The LLM provider to format the tools for
    Returns
    -------
    List[Dict[str, Any]]
        A list of JSON schemas for each tool
    """
    tools_formatted = []
    if mode in {Mode.TOOLS, Mode.MISTRAL_TOOLS}:
        for tool in tools:
            schema = {
                "type": "function",
                "function": openai_schema(tool),
            }
            tools_formatted.append(schema)

    elif mode == Mode.ANTHROPIC_TOOLS:
        for tool in tools:
            schema = anthropic_schema(tool)
            tools_formatted.append(schema)

    else:
        raise ValueError(f"Unknown mode {mode}")

    return tools_formatted