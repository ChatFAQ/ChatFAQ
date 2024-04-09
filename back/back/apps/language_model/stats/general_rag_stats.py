from django.db.models import Subquery
from back.apps.language_model.models import Intent

def calculate_general_rag_stats(prev_messages, num_messages):
        chit_chats_count = prev_messages.filter(messageknowledgeitem__isnull=True).count()
        chit_chats_percentage = chit_chats_count / num_messages * 100

        intents_suggested = Intent.objects.filter(suggested_intent=True).values("pk")

        unanswerable_queries_count = prev_messages.filter(intent__in=Subquery(intents_suggested)).count()
        unanswerable_queries_percentage = unanswerable_queries_count / num_messages * 100

        answerable_queries_count = prev_messages.count() - unanswerable_queries_count
        answerable_queries_percentage = answerable_queries_count / num_messages * 100

        return {
            "chit_chats_count": chit_chats_count,
            "chit_chats_percentage":  round(chit_chats_percentage, 1),
            "unanswerable_queries_count": unanswerable_queries_count,
            "unanswerable_queries_percentage": round(unanswerable_queries_percentage, 1),
            "answerable_queries_count": answerable_queries_count,
            "answerable_queries_percentage": round(answerable_queries_percentage, 1),
        }

