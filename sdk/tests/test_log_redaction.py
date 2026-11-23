import unittest
from unittest.mock import patch

import websockets

from chatfaq_sdk import ChatFAQSDK, _redact_token


class StopConsumer(Exception):
    """Stop the SDK's intentionally infinite consumer loop during tests."""


class FailingConnection:
    """Provide an async context manager that stops after URI inspection."""

    async def __aenter__(self):
        raise StopConsumer

    async def __aexit__(self, exc_type, exc_value, traceback):
        return False


def rendered_log_messages(mock_logger):
    """Render deferred logging arguments so assertions match emitted output."""

    messages = []
    for call in mock_logger.info.call_args_list:
        template, *args = call.args
        messages.append(template % tuple(args) if args else template)
    return messages


class LogRedactionTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.sdk = ChatFAQSDK(
            chatfaq_ws="ws://localhost:8000",
            chatfaq_http="http://localhost:8000",
            token="secret value&with/symbols?",
            fsm_name=None,
        )

    async def test_consumer_encodes_token_without_logging_it(self):
        captured_uri = None

        def connect(uri):
            nonlocal captured_uri
            captured_uri = uri
            return FailingConnection()

        with (
            patch("chatfaq_sdk.websockets.connect", side_effect=connect),
            patch("chatfaq_sdk.logger") as mock_logger,
        ):
            with self.assertRaises(StopConsumer):
                await self.sdk.consumer("ai")

        self.assertEqual(
            captured_uri,
            "ws://localhost:8000/back/ws/broker/ai/"
            "?token=secret+value%26with%2Fsymbols%3F",
        )
        messages = rendered_log_messages(mock_logger)
        self.assertIn(
            "[AI] Connecting to ws://localhost:8000/back/ws/broker/ai/",
            messages,
        )
        self.assertNotIn(self.sdk.token, "\n".join(messages))

    async def test_consumer_redacts_token_from_connection_errors(self):
        error = websockets.WebSocketException(
            "failed ws://localhost:8000/?token=exposed-value&retry=true"
        )

        with (
            patch("chatfaq_sdk.websockets.connect", side_effect=error),
            patch("chatfaq_sdk.asyncio.sleep", side_effect=StopConsumer),
            patch("chatfaq_sdk.logger") as mock_logger,
        ):
            with self.assertRaises(StopConsumer):
                await self.sdk.consumer("rpc")

        messages = "\n".join(rendered_log_messages(mock_logger))
        self.assertNotIn("exposed-value", messages)
        self.assertIn("token=<redacted>&retry=true", messages)

    def test_redaction_handles_token_at_any_query_position(self):
        self.assertEqual(
            _redact_token("wss://example.test/?first=1&token=secret&last=2"),
            "wss://example.test/?first=1&token=<redacted>&last=2",
        )


if __name__ == "__main__":
    unittest.main()
