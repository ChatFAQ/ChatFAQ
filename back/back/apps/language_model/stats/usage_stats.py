from django.db.models import Count, Avg
from back.apps.language_model.models import RAGConfig
from back.apps.broker.models.message import Message, Conversation

def calculate_usage_stats(messages):
    total_messages = messages.count()

    conversations_ids = messages.values('conversation_id').distinct()
    total_conversations = conversations_ids.count()

    # num messages per conversation

    conversations_with_message_count = Conversation.objects.filter(id__in=conversations_ids).annotate(
        messages_count=Count('message')
    )

    average_messages_per_conversation = conversations_with_message_count.aggregate(average_count=Avg('messages_count'))['average_count']

    # get all RAG Config ids
    rag_config_ids = RAGConfig.objects.values_list('id', flat=True)
    # number of messages per RAG Config

    message_counts_per_rag_config = {}
    conversation_counts_per_rag_config = {}

    for rag_config_id_aux in rag_config_ids:
        # Filter messages by RAG config ID within the JSONField
        messages_per_rag = Message.objects.filter(
            stack__contains=[{"type": "lm_generated_text", "payload": {"rag_config_id": str(rag_config_id_aux)}}]
        )

        messages_per_rag_count = messages_per_rag.count()
        conversation_per_rag_count = messages_per_rag.values('conversation_id').distinct().count()

        rag_config_name = RAGConfig.objects.get(pk=rag_config_id_aux).name
        
        # Store the count for this RAG config ID
        message_counts_per_rag_config[rag_config_name] = messages_per_rag_count
        conversation_counts_per_rag_config[rag_config_name] = conversation_per_rag_count


    usage_stats = {
        "total_messages": total_messages, # int
        "total_conversations": total_conversations, # int
        "average_messages_per_conversation": average_messages_per_conversation, # float
        "message_counts_per_rag_config": message_counts_per_rag_config, # dict[str, int]
        "conversation_counts_per_rag_config": conversation_counts_per_rag_config # dict[str, int]
    }

    return usage_stats