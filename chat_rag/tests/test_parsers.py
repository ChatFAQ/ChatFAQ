import builtins
import unittest
from unittest.mock import patch

from chat_rag.data.parsers import (
    ParsingUnavailableError,
    parse_html,
    parse_pdf,
)


_ORIGINAL_IMPORT = builtins.__import__


def _import_without_unstructured(name, *args, **kwargs):
    """Simulate the unsupported parser stack without changing the environment."""
    if name == "unstructured" or name.startswith("unstructured."):
        raise ModuleNotFoundError(
            "No module named 'unstructured'",
            name="unstructured",
        )
    return _ORIGINAL_IMPORT(name, *args, **kwargs)


class ParserCompatibilityTests(unittest.TestCase):
    """Verify parser entry points explain the Python compatibility limitation."""

    def test_parser_entry_points_raise_actionable_error(self):
        for parser in (parse_pdf, parse_html):
            with self.subTest(parser=parser.__name__):
                with patch(
                    "builtins.__import__",
                    side_effect=_import_without_unstructured,
                ):
                    with self.assertRaisesRegex(
                        ParsingUnavailableError,
                        (
                            r"unavailable in chat-rag 0\.2\.15 on Python 3\.14"
                            r".*previous chat-rag manifest constrained "
                            r"`unstructured` to Python <3\.12"
                        ),
                    ):
                        parser()


if __name__ == "__main__":
    unittest.main()
