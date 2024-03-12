from datetime import datetime
from io import BytesIO
from zipfile import ZipFile

from django.db.models.functions import Trunc
from django.db.models import Count

from django.http import HttpResponse, JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny

from ..models import ConsumerRoundRobinQueue
from ..models.message import AdminReview, AgentType, Conversation, Message, UserFeedback
from ..serializers import (
    AdminReviewSerializer,
    ConversationMessagesSerializer,
    UserFeedbackSerializer, ConversationSerializer, StatsSerializer, ConsumerRoundRobinQueueSerializer
)
from ..serializers.messages import MessageSerializer
import django_filters

from ...language_model.models import RAGConfig, Intent
from ...language_model.stats import calculate_response_stats, calculate_general_rag_stats
from django.db.models import Q


class ConversationFilterSet(django_filters.FilterSet):
    rag = django_filters.CharFilter(method='filter_rag')
    reviewed = django_filters.CharFilter(method='filter_reviewed')

    class Meta:
        model = Conversation
        fields = {
           'created_date': ['lte', 'gte'],
           'id': ['exact'],
        }

    def filter_rag(self, queryset, name, value):
        rag = RAGConfig.objects.filter(pk=value).first()
        return queryset.filter(message__stack__0__payload__rag_config_name=rag.name).distinct()

    def filter_reviewed(self, queryset, name, value):
        val = True
        if value == "completed":
            val = False
        if val:
            return queryset.filter(message__adminreview__isnull=val).exclude(message__adminreview__isnull=not val).distinct()
        return queryset.filter(message__adminreview__isnull=val).distinct()


class ConversationAPIViewSet(
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name']
    filterset_class = ConversationFilterSet

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ConversationMessagesSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action == 'retrieve' or self.action == 'destroy' or 'update' in self.action:
            return [AllowAny(), ]
        return super(ConversationAPIViewSet, self).get_permissions()

    @action(methods=("get",), detail=False, authentication_classes=[], permission_classes=[AllowAny])
    def from_sender(self, request, *args, **kwargs):
        if not request.query_params.get("sender"):
            return JsonResponse(
                {"error": "sender is required"},
                status=400,
            )
        results = [ConversationSerializer(c).data for c in Conversation.conversations_from_sender(request.query_params.get("sender"))]
        return JsonResponse(
            results,
            safe=False,
        )

    @action(methods=("post",), detail=True, authentication_classes=[], permission_classes=[AllowAny])
    def download(self, request, *args, **kwargs):
        """
        A view to download all the knowledge base's items as a csv file:
        """
        ids = kwargs["pk"].split(",")
        if len(ids) == 1:
            conv = Conversation.objects.get(pk=ids[0])
            content = conv.conversation_to_text()
            filename = f"{conv.created_date.strftime('%Y-%m-%d_%H-%M-%S')}.txt"
            content_type = "text/plain"
        else:
            zip_content = BytesIO()
            with ZipFile(zip_content, "w") as _zip:
                for _id in ids:
                    conv = Conversation.objects.get(pk=_id)
                    _content = conv.conversation_to_text()
                    _zip.writestr(
                        conv.get_first_msg().created_date.strftime("%Y-%m-%d_%H-%M-%S")
                        + ".txt",
                        _content,
                    )

            filename = f"{datetime.today().strftime('%Y-%m-%d_%H-%M-%S')}.zip"
            content_type = "application/x-zip-compressed"
            content = zip_content.getvalue()

        response = HttpResponse(content, content_type=content_type)
        response["Content-Disposition"] = "attachment; filename={0}".format(filename)
        response["Access-Control-Expose-Headers"] = "Content-Disposition"
        return response


class MessageView(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    serializer_class = MessageSerializer
    filterset_fields = ["id"]


class UserFeedbackAPIViewSet(viewsets.ModelViewSet):
    serializer_class = UserFeedbackSerializer
    queryset = UserFeedback.objects.all()
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["id", "message"]


class AdminReviewAPIViewSet(viewsets.ModelViewSet):
    serializer_class = AdminReviewSerializer
    queryset = AdminReview.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["id", "message"]


class SenderAPIView(CreateAPIView, UpdateAPIView):
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["id", "message"]

    def get(self, request):
        return JsonResponse(
            list(
                Message.objects.filter(sender__type=AgentType.human.value)
                .values_list("sender__id", flat=True)
                .distinct()
            ),
            safe=False,
        )


class ConsumerRoundRobinQueueViewSet(mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):
    serializer_class = ConsumerRoundRobinQueueSerializer
    queryset = ConsumerRoundRobinQueue.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["id"]


class Stats(APIView):
    def get(self, request):
        serializer = StatsSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        if not RAGConfig.objects.filter(pk=data["rag"]).exists():
            return JsonResponse(
                {"error": "RAG config not found"},
                status=400,
            )
        rag = RAGConfig.objects.get(pk=data["rag"])
        min_date = data.get("min_date", None)
        max_date = data.get("max_date", None)
        granularity = data.get("granularity", None)

        # ----------- Conversations -----------
        conversations = Conversation.objects
        if min_date:
            conversations = conversations.filter(created_date__gte=min_date)
        if max_date:
            conversations = conversations.filter(created_date__lte=max_date)

        conversations_rag_filtered = conversations.filter(
            message__stack__0__payload__rag_config_id=str(rag.id)
        ).distinct()
        # --- Total conversations
        total_conversations = conversations_rag_filtered.count()
        # --- Message count per conversation
        conversations_message_count = conversations_rag_filtered.annotate(
            count=Count("message")
        ).values("count", "name")
        # --- Conversations by date
        conversations_by_date = conversations_rag_filtered.annotate(
            date=Trunc("created_date", granularity)
        ).values("created_date").annotate(count=Count("id"))

        # --- Conversations per RAG Config
        conversations_per_rag = conversations.filter(
            message__stack__0__payload__rag_config_id__isnull=False
        ).annotate(
            rag_id=Count("message__stack__0__payload__rag_config_id")
        ).values("message__stack__0__payload__rag_config_id")

        # ----------- Messages -----------
        messages = Message.objects
        if min_date:
            messages = messages.filter(created_date__gte=min_date)
        if max_date:
            messages = messages.filter(created_date__lte=max_date)
        messages_rag_filtered = messages.filter(
            stack__0__payload__rag_config_id=str(rag.id)
        ).distinct()
        # --- Messages per RAG Config
        messages_per_rag = Message.objects.filter(
            stack__0__payload__rag_config_id__isnull=False
        ).annotate(
            rag_id=Count("stack__0__payload__rag_config_id")
        ).values("stack__0__payload__rag_config_id").annotate(count=Count("stack__0__payload__rag_config_id"))
        messages_with_prev = messages.filter(prev__isnull=False)
        general_stats = calculate_general_rag_stats(messages_with_prev, messages_with_prev.count())
        # ----------- Reviews and Feedbacks -----------
        admin_reviews = AdminReview.objects.filter(message__in=messages_rag_filtered)
        user_feedbacks = UserFeedback.objects.filter(message__in=messages_rag_filtered, value__isnull=False)
        reviews_and_feedbacks = calculate_response_stats(admin_reviews, user_feedbacks)

        positive_admin_reviews = admin_reviews.filter(ki_review_data__contains=[{"value": "positive"}]).count()
        total_admin_reviews = admin_reviews.filter(
            Q(ki_review_data__contains=[{"value": "positive"}]) | Q(ki_review_data__contains=[{"value": "negative"}])
        ).count()
        total_admin_relevant_reviews = admin_reviews.filter(
            Q(ki_review_data__contains=[{"value": "positive"}]) | Q(ki_review_data__contains=[{"value": "alternative"}])
        ).count()
        precision = positive_admin_reviews / total_admin_reviews if total_admin_reviews > 0 else 0
        recall = positive_admin_reviews / total_admin_relevant_reviews if total_admin_relevant_reviews > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        return JsonResponse(
            {
                "total_conversations": total_conversations,
                # "conversations_per_rag": list(conversations_per_rag.all()),
                "conversations_message_count": list(conversations_message_count.all()),
                "messages_per_rag": list(messages_per_rag.all()),
                "conversations_by_date": list(conversations_by_date.all()),
                **general_stats,
                **reviews_and_feedbacks,
                "precision": round(precision, 2),
                "recall": round(recall, 2),
                "f1": round(f1, 2),
            },
            safe=False,
        )
