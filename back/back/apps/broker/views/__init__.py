from datetime import datetime
from io import BytesIO
from zipfile import ZipFile

import django_filters
from django.db.models import Avg, Count, Q
from django.db.models.functions import Trunc
from django.http import HttpResponse, JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet

from ...language_model.stats import calculate_general_stats, calculate_response_stats
from ..models import ConsumerRoundRobinQueue
from ..models.message import AdminReview, AgentType, Conversation, Message, UserFeedback
from ..serializers import (
    AdminReviewSerializer,
    ConsumerRoundRobinQueueSerializer,
    ConversationMessagesSerializer,
    ConversationSerializer,
    StatsSerializer,
    UserFeedbackSerializer,
)
from ..serializers.messages import MessageSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage


class ConversationFilterSet(django_filters.FilterSet):
    reviewed = django_filters.CharFilter(method='filter_reviewed')
    fsm_def = django_filters.CharFilter(method='filter_fsm_def')

    class Meta:
        model = Conversation
        fields = {
           'created_date': ['lte', 'gte'],
           'id': ['exact'],
        }

    def filter_fsm_def(self, queryset, name, value):
        return queryset.filter(message__stack__0__contains=[{'fsm_definition': value}]).distinct()

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
        if self.action is not None and (self.action == 'retrieve' or self.action == 'destroy' or 'update' in self.action):
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

    @action(methods=("get",), detail=True)
    def review_progress(self, request, pk=None):
        conv = Conversation.objects.get(pk=pk)
        return JsonResponse(
            conv.get_review_progress(),
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
    filterset_fields = ["id", "intent__id"]


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
        min_date = data.get("min_date", None)
        max_date = data.get("max_date", None)
        granularity = data.get("granularity", None)

        # ----------- Conversations -----------
        conversations = Conversation.objects
        if min_date:
            conversations = conversations.filter(created_date__gte=min_date)
        if max_date:
            conversations = conversations.filter(created_date__lte=max_date)


        # --- Total conversations
        total_conversations = conversations.count()
        # --- Message count per conversation
        conversations_message_count = conversations.annotate(
            count=Count("message")
        ).values("count", "name")
        # average of conversations_message_count
        conversations_message_avg = conversations.annotate(
            count=Count("message")
        ).aggregate(avg=Avg("count"))
        # --- Conversations by date
        conversations_by_date = conversations.annotate(
            date=Trunc("created_date", granularity)
        ).values("created_date").annotate(count=Count("id"))

        # ----------- Messages -----------
        messages = Message.objects
        if min_date:
            messages = messages.filter(created_date__gte=min_date)
        if max_date:
            messages = messages.filter(created_date__lte=max_date)

        messages = messages.all()


        messages_with_prev = messages.filter(prev__isnull=False)
        general_stats = calculate_general_stats(messages_with_prev, messages_with_prev.count())
        # ----------- Reviews and Feedbacks -----------
        admin_reviews = AdminReview.objects.filter(message__in=messages)
        user_feedbacks = UserFeedback.objects.filter(message__in=messages, value__isnull=False)
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
                "conversations_message_count": list(conversations_message_count.all()),
                "conversations_message_avg": round(conversations_message_avg.get('avg'), 2) if conversations_message_avg is not None else None,
                "total_messages": messages.count(),  # Change this line
                "conversations_by_date": list(conversations_by_date.all()),
                **general_stats,
                **reviews_and_feedbacks,
                "precision": round(precision, 2) if precision is not None else None,
                "recall": round(recall, 2) if recall is not None else None,
                "f1": round(f1, 2) if f1 is not None else None,
            },
            safe=False,
        )


class FileUploadView(APIView):
    def post(self, request, format=None):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        # Save the file
        file_name = default_storage.save(file.name, file)
        file_url = default_storage.url(file_name)

        return Response({'url': file_url}, status=status.HTTP_201_CREATED)
