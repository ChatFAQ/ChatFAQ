"""
This file is for utility functions that step definitions may need.
"""

import re
from typing import List


def remove_model_w_template_engine_keywords(text: str) -> str:
    """
    Used to remove lines beginning with `# ::` as used in ModelW templates
    Note: The line may have whitespace before the `#` and after the `::`
    """
    return re.sub(r"^\s*# ::.*\n", "", text, flags=re.MULTILINE)


def split_on_pipes(text: str) -> List[str]:
    """
    Splits a string on pipes and returns a list of the results

    Note: Escaped pipes are ignored (ie. `\|` is not treated as a pipe)
          And leading and trailing whitespace is removed from each item
          And empty start and end items are removed

    Args:
        text (str): The text to split

    Returns:
        List[str]: The list of items

    Example:
        split_on_pipes("  | a | b | c |  ") -> ["a", "b", "c"]
    """
    split = [item.strip() for item in re.split(r"(?<!\\)\|", text)]

    # Remove splits from before the first pipe and after the last pipe
    if len(split) >= 2:
        return split[1:-1]


def parse_datatable_string(datatable_string: str, vertical=False):
    """
    As pytest-bdd doesn't support data tables, we need to do it manually,
    as data tables are very useful for testing, and we'd be seriously limited
    without them.

    """
    # Remove ModelW template engine keywords
    datatable_string = remove_model_w_template_engine_keywords(datatable_string)
    # Split the string into lines
    lines = datatable_string.strip().split("\n")
    # Remove leading and trailing whitespace from each line
    lines = [line.strip() for line in lines]

    if vertical:
        data = [split_on_pipes(line) for line in lines]
        data_dict: dict[str, str] = {}
        for item in data:
            key = item[0].strip()
            value = item[1].strip() if len(item) > 1 else ""
            data_dict[key] = value

        return data_dict
    else:
        # Extract headers from the first line
        headers = split_on_pipes(lines[0])

        # Extract rows from the remaining lines
        rows: List[dict[str, str]] = []
        for line in lines[1:]:
            values = split_on_pipes(line)
            if len(values) < len(headers):
                values.extend(
                    [""] * (len(headers) - len(values))
                )  # Extend values to match headers length
            row = dict(zip(headers, values))
            rows.append(row)

        return rows


def get_datatable_from_step_name(step_name: str):
    """
    Returns the data table string from the step name
    """
    return step_name.split("\n", 1)[-1] if "\n" in step_name else None


def cast_to_bool(text: str) -> bool:
    """
    Casts a string to a boolean

    Useful for string values in datatables that need to be treated as boolean

    Args:
        text (str): The text to cast
    """
    TRUE = [
        "true",
        "yes",
        "1",
        "y",
        "x",
        "[x]",
        "on",
        "enable",
        "enabled",
        "active",
        "success",
    ]
    FALSE = [
        "false",
        "no",
        "0",
        "",
        "[]",
        "[ ]",
        "n",
        "off",
        "disable",
        "disabled",
        "inactive",
        "failure",
    ]

    if text.lower() not in TRUE + FALSE:
        raise ValueError(
            f"Cannot cast '{text}' to a boolean.  Please use one of {TRUE} or {FALSE}, or extend cast_to_bool()"
        )

    return text.lower() in TRUE
