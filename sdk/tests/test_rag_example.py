from unittest import TestCase

from examples.rag_example.fsm_definition import _text_content_for_retrieval


class TextContentForRetrievalTest(TestCase):
    """Cover text normalization before semantic retrieval."""

    def test_extracts_only_text_from_multimodal_content(self):
        content = [
            {"type": "text", "text": "What is"},
            {"type": "tool_use", "tool_use": {"name": "ignored"}},
            {"type": "text", "text": "ChatFAQ?"},
        ]

        self.assertEqual(_text_content_for_retrieval(content), "What is ChatFAQ?")

    def test_preserves_legacy_string_content(self):
        self.assertEqual(
            _text_content_for_retrieval("What is ChatFAQ?"),
            "What is ChatFAQ?",
        )
