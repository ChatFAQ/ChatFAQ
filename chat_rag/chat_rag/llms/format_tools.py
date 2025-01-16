# This file contains code adapted from the instructor package given that the package is incompatible with the version of rich that is required by ChatFAQ current environment.
# Original author: Jason Liu
# Source: https://github.com/jxnl/instructor
# License: MIT (https://github.com/jxnl/instructor/blob/main/LICENSE)

import enum
from typing import Any, Dict, List, Union

from docstring_parser import parse
from pydantic import BaseModel


class Mode(enum.Enum):
    """The mode to use for patching the client"""

    TOOLS = "tool_call"
    MISTRAL_TOOLS = "mistral_tools"
    ANTHROPIC_TOOLS = "anthropic_tools"
    GEMINI_TOOLS = "gemini_tools"


def openai_schema(model: Union[BaseModel, Dict]) -> Dict[str, Any]:
    """
    Return the schema in the format of OpenAI's schema as jsonschema

    Note:
        Its important to add a docstring to describe how to best use this class, it will be included in the description attribute and be part of the prompt.

    Returns:
        model_json_schema (dict): A dictionary in the format of OpenAI's schema as jsonschema
    """
    if not isinstance(model, Dict): # 
        schema = model.model_json_schema()
    else:
        schema = model

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


def anthropic_schema(model: Union[BaseModel, Dict]) -> Dict[str, Any]:
    """
    Return the schema in the format of Anthropic's schema
    """
    schema = openai_schema(model)
    return {
        "name": schema["name"],
        "description": schema["description"],
        "input_schema": model.model_json_schema() if isinstance(model, BaseModel) else model,
    }

def gemini_schema(model: Union[BaseModel, Dict]) -> Dict[str, Any]:
    """
    Return the schema in the format of Gemini's schema
    """
    schema = openai_schema(model)
    parameters = schema["parameters"]
    parameters = uppercase_types_recursively(parameters)
    schema = {
        "name": schema["name"],
        "description": schema["description"],
        "parameters": parameters,
    }
    return schema

def uppercase_types_recursively(schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively uppercase the type values in the schema and remove the title attribute to match the Open API 3.0 spec that the google genai library requires.
    """
    if isinstance(schema, dict):
        if "type" in schema:
            schema["type"] = schema["type"].upper()
        if "title" in schema:
            del schema["title"]
        for key, value in schema.items():
            schema[key] = uppercase_types_recursively(value)
    elif isinstance(schema, list):
        for i, item in enumerate(schema):
            schema[i] = uppercase_types_recursively(item)
    return schema


def format_tools(tools: List[Union[BaseModel, Dict]], mode: Mode) -> List[Dict[str, Any]]:
    """
    Given a series of Pydantic models, return the JSON schema required by each LLM provider.
    Parameters
    ----------
    tools : List[Union[BaseModel, Dict]]
        A list of Pydantic models or theirs model_json_schema
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

    elif mode == Mode.GEMINI_TOOLS:
        for tool in tools:
            schema = gemini_schema(tool)
            tools_formatted.append(schema)

    else:
        raise ValueError(f"Unknown mode {mode}")

    return tools_formatted