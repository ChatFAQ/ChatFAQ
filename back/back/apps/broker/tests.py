from django.test import SimpleTestCase

from back.apps.broker.serializers.rpc import RPCRetrieverRequestSerializer


class RPCRetrieverRequestSerializerTest(SimpleTestCase):
    """Ensure retriever requests retain SDK correlation metadata."""

    def test_preserves_bot_channel_name(self):
        serializer = RPCRetrieverRequestSerializer(
            data={
                "retriever_config_name": "chatfaq_retriever",
                "bot_channel_name": "dev:channels:specific.conversation",
                "query": "What is ChatFAQ?",
                "top_k": 3,
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(
            serializer.validated_data["bot_channel_name"],
            "dev:channels:specific.conversation",
        )
