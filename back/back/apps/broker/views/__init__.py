from datetime import datetime
from io import BytesIO
from zipfile import ZipFile

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from rest_framework import mixins, viewsets
from rest_framework.decorators import action, permission_classes
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from ..models.message import AdminReview, AgentType, Conversation, Message, UserFeedback
from ..serializers import (
    AdminReviewSerializer,
    ConversationMessagesSerializer,
    UserFeedbackSerializer, ConversationSerializer,
)
from ..serializers.messages import MessageSerializer


class ConversationAPIViewSet(
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ConversationMessagesSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action == 'retrieve' or self.action == 'destroy':
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


class MessageView(LoginRequiredMixin, viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


class UserFeedbackAPIViewSet(viewsets.ModelViewSet):
    serializer_class = UserFeedbackSerializer
    queryset = UserFeedback.objects.all()
    permission_classes = [AllowAny]
    filterset_fields = ["message"]


class AdminReviewAPIViewSet(viewsets.ModelViewSet):
    serializer_class = AdminReviewSerializer
    queryset = AdminReview.objects.all()


class SenderAPIView(CreateAPIView, UpdateAPIView):
    def get(self, request):
        return JsonResponse(
            list(
                Message.objects.filter(sender__type=AgentType.human.value)
                .values_list("sender__id", flat=True)
                .distinct()
            ),
            safe=False,
        )
