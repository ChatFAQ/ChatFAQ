from rest_framework.generics import CreateAPIView, UpdateAPIView
from zipfile import ZipFile

from io import BytesIO

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse
from rest_framework import viewsets, generics

from ..models.message import Message, UserFeedback, AgentType, AdminReview
from ..serializers import UserFeedbackSerializer, AdminReviewSerializer
from ..serializers.messages import MessageSerializer
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response


class ConversationAPIViewSet(mixins.RetrieveModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   # mixins.UpdateModelMixin,
                   viewsets.GenericViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def retrieve(self, request, *args, **kwargs):
        return JsonResponse(
            Message.get_mml_chain(kwargs["pk"]), safe=False
        )

    def destroy(self, request, *args, **kwargs):
        Message.delete_conversations(kwargs["pk"].split(","))
        return Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        # get any query params from request
        return JsonResponse(
            Message.conversations_info(request.query_params.get("sender")), safe=False
        )

    # def update(self, request, *args, **kwargs):
    #     request.data

    @action(methods=('post',), detail=True)
    def download(self, request, *args, **kwargs):
        """
        A view to download all the dataset's items as a csv file:
        """
        ids = kwargs["pk"].split(",")
        if len(ids) == 1:
            content = Message.conversation_to_text(ids[0])
            filename = f"{Message.get_first_msg(ids[0]).send_time.strftime('%Y-%m-%d_%H-%M-%S')}.txt"
            content_type = 'text/plain'
        else:
            zip_content = BytesIO()
            with ZipFile(zip_content, 'w') as _zip:
                for _id in ids:
                    _content = Message.conversation_to_text(_id)
                    _zip.writestr(Message.get_first_msg(_id).send_time.strftime('%Y-%m-%d_%H-%M-%S') + ".txt", _content)

            filename = f"{Message.get_first_msg(ids[0]).send_time.strftime('%Y-%m-%d_%H-%M-%S')}.zip"
            content_type = 'application/x-zip-compressed'
            content = zip_content.getvalue()

        response = HttpResponse(content, content_type=content_type)
        response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
        response['Access-Control-Expose-Headers'] = 'Content-Disposition'
        return response


class MessageView(LoginRequiredMixin, viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


class UserFeedbackAPIView(CreateAPIView, UpdateAPIView):
    serializer_class = UserFeedbackSerializer
    queryset = UserFeedback.objects.all()


class AdminReviewAPIView(generics.ListCreateAPIView):
    serializer_class = AdminReviewSerializer
    queryset = AdminReview.objects.all()


class SenderAPIView(CreateAPIView, UpdateAPIView):
    def get(self, request):
        return JsonResponse(
            list(Message.objects.filter(
                sender__type=AgentType.human.value
            ).values_list(
                "sender__id", flat=True
            ).distinct()),
            safe=False
        )
