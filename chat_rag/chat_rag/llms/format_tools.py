import enum
import inspect
from typing import Any, Callable, Dict, List, Union


def function_to_json(func) -> dict:
    """
    Converts a Python function into a JSON-serializable dictionary
    that describes the function's signature, including its name,
    description, and parameters.
    Function from https://github.com/openai/swarm

    Args:
        func: The function to be converted.

    Returns:
        A dictionary representing the function's signature in JSON format.
    """
    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
        type(None): "null",
    }

    try:
        signature = inspect.signature(func)
    except ValueError as e:
        raise ValueError(
            f"Failed to get signature for function {func.__name__}: {str(e)}"
        )

    parameters = {}
    for param in signature.parameters.values():
        try:
            param_type = type_map.get(param.annotation, "string")
        except KeyError as e:
            raise KeyError(
                f"Unknown type annotation {param.annotation} for parameter {param.name}: {str(e)}"
            )
        parameters[param.name] = {"type": param_type}

    required = [
        param.name
        for param in signature.parameters.values()
        if param.default == inspect._empty
    ]

    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": func.__doc__ or "",
            "parameters": {
                "type": "object",
                "properties": parameters,
                "required": required,
            },
        },
    }


class Mode(enum.Enum):
    """The mode to use for patching the client"""

    OPENAI_TOOLS = "openai_tools"
    MISTRAL_TOOLS = "mistral_tools"
    ANTHROPIC_TOOLS = "anthropic_tools"
    GEMINI_TOOLS = "gemini_tools"


def anthropic_schema(schema: Dict) -> Dict[str, Any]:
    """
    Return the schema in the format of Anthropic's schema
    """
    schema = schema["function"]
    return {
        "name": schema["name"],
        "description": schema["description"],
        "input_schema": schema["parameters"],
    }


def gemini_schema(schema: Dict) -> Dict[str, Any]:
    """
    Return the schema in the format of Gemini's schema
    """
    schema = schema["function"]
    schema = {
        "name": schema["name"],
        "description": schema["description"],
        "parameters": uppercase_types_recursively(schema["parameters"]),
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


def format_tools(
    tools: List[Union[Callable, Dict]], mode: Mode
) -> List[Dict[str, Any]]:
    """
    Given a series of functions, return the JSON schema required by each LLM provider.
    Parameters
    ----------
    tools : List[Union[Callable, Dict]]
        A list of tools in the OpenAI JSON format or a callable function.
    mode : Mode
        The LLM provider to format the tools for
    Returns
    -------
    List[Dict[str, Any]]
        A list of JSON schemas for each tool
    """
    # first convert to the openai dict format if they are a callable
    tools = [function_to_json(tool) if callable(tool) else tool for tool in tools]
    tools_formatted = []
    if mode in {Mode.OPENAI_TOOLS, Mode.MISTRAL_TOOLS}:
        for tool in tools:
            tools_formatted.append(tool)

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
