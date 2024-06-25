from html import unescape
from typing import List, TypedDict


class SingletonMeta(type):
    """
    A General purpose singleton class.

    To be used as a metaclass for a class that should
    only have one instance.

    Example:
    ```
    class MyClass(metaclass=SingletonMeta):
        pass
    ```
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        If the class has not been instantiated, create an instance
        and store it in the _instances dictionary.
        Otherwise, return the instance that has already been created.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class DatatableRow(TypedDict):
    cells: List[str]


class ReportDatatable(TypedDict):
    rows: List[DatatableRow]


def datatable_to_arguments(
    datatable: dict[str, str] | list[dict[str, str]]
) -> ReportDatatable:
    """
    Converts a datatable to a format that can be displayed nicely in the report.
    The standard format for a datatable is a dictionary of rows and cells.

    Note: We can accept horizontal and vertical datatables.
          A vertical datatable is a dictionary of key-value pairs.
          A horizontal datatable is a list of dictionaries.

    Example:
    ```gherkin
        Given the following vertical datatable:
        | key1    | value1  |
        | key2    | value2  |
    ```
    Example:
    ```gherkin
        Given the following horizontal datatable:
        | key1   | key2   |
        | value1 | value2 |
    ```

    Args:
        datatable (dict[str, str] | list[dict[str, str]]): The datatable to convert

    Returns:
        dict[rows:
    """

    if isinstance(datatable, dict):
        keys = [unescape(key) for key in datatable.keys()]
        values = [unescape(value) for value in datatable.values()]
        rows = [{"cells": keys}, {"cells": values}]
    else:
        rows = [
            {"cells": [unescape(key) for key in row.keys()]} for row in datatable[:1]
        ]
        rows.extend(
            [{"cells": [unescape(key) for key in row.values()]} for row in datatable]
        )
    return {"rows": rows}
