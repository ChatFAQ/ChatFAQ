from logging import getLogger

from django.apps import apps
from django.db.models import F
import ray


logger = getLogger(__name__)


@ray.remote(num_cpus=0.2, resources={"tasks": 1})
def calculate_rag_stats_task(rag_config_id, dates_ranges=[(None, None)]):
    """
    Compute the statistics for a knowledge base.
    Parameters
    ----------
    rag_config_id : int
        The primary key of the RAGConfig object.
    dates_ranges : list
        A list of tuples with the start and end dates for the statistics.
    """
    # TODO: add the % of unlabeled knowledge items
    # TODO: add the % of unlabeled responses

    from datetime import datetime

    from back.apps.language_model.stats import (
        calculate_general_rag_stats,
        calculate_response_stats,
        calculate_retriever_stats,
    )

    Message = apps.get_model("broker", "Message")
    AdminReview = apps.get_model("broker", "AdminReview")
    UserFeedback = apps.get_model("broker", "UserFeedback")


    all_retriever_stats = []
    all_quality_stats = []
    all_general_stats = []

    for start_date_str, end_date_str in dates_ranges:

        # else all the messages
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d") if start_date_str else None
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d") if end_date_str else None

        logger.info(f"Start date: {start_date}, end date: {end_date}")

        messages = Message.objects.filter(
            stack__contains=[
            {"type": "lm_generated_text", "payload": {"rag_config_id": str(rag_config_id)}}
        ]
        )

        if start_date is not None:  # Apply start_date if not None
            messages = messages.filter(created_date__gte=start_date)

        if end_date is not None:   # Apply end_date if not None
            messages = messages.filter(created_date__lte=end_date)

        ##############################
        # Retriever stats
        ##############################

        admin_reviews = AdminReview.objects.filter(
            message__in=messages,
        )

        ki_review_data_list = [admin_review.ki_review_data for admin_review in admin_reviews]

        logger.info(f"Number of admin reviews: {admin_reviews.count()}")

        retriever_stats = calculate_retriever_stats(ki_review_data_list)

        all_retriever_stats.append(retriever_stats)

        # print retriever stats
        for k, v in retriever_stats.items():
            logger.info(f"{k}: {v:.2f}")

        ##############################
        # Response quality stats
        ##############################

        user_feedbacks = UserFeedback.objects.filter(
            message__in=messages,
            value__isnull=False,
        )

        response_stats = calculate_response_stats(admin_reviews, user_feedbacks)

        for k, v in response_stats.items():
            logger.info(f"{k}: {v:.2f}")

        all_quality_stats.append(response_stats)

        ##############################
        # General RAG stats
        ##############################

        prev_messages_ids = messages.annotate(previous_message_id=F('prev__id'))\
                                    .values('prev_id')\
                                    .filter(previous_message_id__isnull=False)

        prev_messages = Message.objects.filter(id__in=prev_messages_ids)

        general_rag_stats = calculate_general_rag_stats(prev_messages, messages.count())

        for k, v in general_rag_stats.items():
            logger.info(f"{k}: {v:.2f}")

        all_general_stats.append(general_rag_stats)


    # TODO: Return the stats to the frontend


@ray.remote(num_cpus=0.2, resources={"tasks": 1})
def calculate_usage_stats_task(rag_config_id=None, dates_ranges=[(None, None)]):
    """
    Compute the usage statistics related to the number of messages, conversations, etc.
    Parameters
    ----------
    rag_config_id : int
        The primary key of the RAGConfig object to calculate the usage stats for. If None, the stats will be calculated for all the historical data.
    dates_ranges : list
        A list of tuples with the start and end dates for the statistics.
    """

    from datetime import datetime

    from back.apps.language_model.stats import calculate_usage_stats

    Message = apps.get_model("broker", "Message")

    all_usage_stats = []

    for start_date_str, end_date_str in dates_ranges:

        # else all the messages
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d") if start_date_str else None
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d") if end_date_str else None

        logger.info(f"Start date: {start_date}, end date: {end_date}")

        messages = Message.objects.all()

        if rag_config_id:
            messages = messages.filter(stack__contains=[
                {"type": "lm_generated_text", "payload": {"rag_config_id": str(rag_config_id)}}
            ])

        if start_date is not None:  # Apply start_date if not None
            messages = messages.filter(created_date__gte=start_date)

        if end_date is not None:   # Apply end_date if not None
            messages = messages.filter(created_date__lte=end_date)

        usage_stats = calculate_usage_stats(messages)

        for k, v in usage_stats.items():
            logger.info(f"{k}: {v}")

        all_usage_stats.append(usage_stats)
