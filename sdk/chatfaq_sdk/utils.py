import inspect
from typing import Dict, List

ROLES_MAP = {
    "bot": "assistant",
    "human": "user",
}


def convert_mml_to_llm_format(mml: List[Dict]) -> List[Dict]:
    """
    Converts the MML (Message Markup Language) format to the common LLM message format.
    Analogous to format_msgs_chain_to_llm_context in back/back/apps/language_model/consumers/__init__.py


    :param mml: List of messages in MML format
    :return: List of messages in LLM format {'role': 'user', 'content': '...'}
    """
    aggregated_messages = []
    current_role = None  # "user" for human and "assistant" for bot
    aggregated_contents = []  # list of Content objects for the current group

    def process_stack(stack: Dict) -> List[Dict]:
        """
        Process a single stack item into a list of LLM message format.
        """
        contents = []
        type = stack.get("type")

        if type == "message":
            contents.append(
                {
                    "type": "text",
                    "text": stack["payload"]["content"],
                }
            )
        elif type == "tool_use":
            contents.append(
                {
                    "type": "tool_use",
                    "tool_use": stack["payload"],
                }
            )
        elif type == "tool_result":
            contents.append(
                {
                    "type": "tool_result",
                    "tool_result": stack["payload"],
                }
            )

        return contents

    def process_msg(msg: Dict) -> List[Dict]:
        """
        Process each broker message into a list of LLM message format by iterating over its stacks.
        """
        contents = []
        for stack in msg.get("stack", []):
            contents.extend(process_stack(stack))
        return contents

    def merge_contents(existing: List[Dict], new: List[Dict]) -> List[Dict]:
        """
        Merge two lists of LLM message format.
        If the last element of the existing list and the first element of the new list are both text,
        then they are concatenated.
        """
        if not existing:
            return new
        if not new:
            return existing

        merged = existing.copy()
        if merged and new and merged[-1]["type"] == "text" and new[0]["type"] == "text":
            merged[-1]["text"] = (
                merged[-1]["text"].strip() + " " + new[0]["text"].strip()
            )
            merged.extend(new[1:])
        else:
            merged.extend(new)
        return merged

    for msg in mml:
        role = ROLES_MAP[msg["sender"]["type"]]
        msg_contents = process_msg(msg)
        if not msg_contents:
            continue

        if current_role is None:
            current_role = role
            aggregated_contents = msg_contents
        elif current_role == role:
            aggregated_contents = merge_contents(aggregated_contents, msg_contents)
        else:
            aggregated_messages.append(
                {
                    "role": current_role,
                    "content": aggregated_contents,
                }
            )
            current_role = role
            aggregated_contents = msg_contents

    if aggregated_contents:
        aggregated_messages.append(
            {
                "role": current_role,
                "content": aggregated_contents,
            }
        )

    return aggregated_messages


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
