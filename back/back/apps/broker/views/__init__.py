from rest_framework.generics import CreateAPIView, UpdateAPIView
from zipfile import ZipFile

from io import BytesIO

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse
from rest_framework import viewsets
from rest_framework.views import APIView

from ..models.message import Message, Vote, AgentType
from ..serializers import IdSerializer, IdsSerializer, VoteSerializer
from ..serializers.messages import MessageSerializer


class MessageView(LoginRequiredMixin, viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


class ConversationView(APIView):
    def get(self, request):
        s = IdSerializer(data=request.GET)
        s.is_valid(raise_exception=True)
        return JsonResponse(
            Message.get_mml_chain(s.data["id"]), safe=False
        )

    def delete(self, request):
        s = IdSerializer(data=request.GET)
        s.is_valid(raise_exception=True)
        Message.delete_conversation()


class ConversationsInfoView(APIView):
    def get(self, request):
        s = IdSerializer(data=request.GET)
        s.is_valid(raise_exception=True)
        return JsonResponse(
            Message.conversations_info(s.data["id"]), safe=False
        )

    def delete(self, request):
        s = IdsSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        Message.delete_conversations(s.data["ids"])
        return JsonResponse({})


class ConversationsDownload(APIView):

    def post(self, request):
        s = IdsSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        if len(s.data["ids"]) == 1:
            content = Message.conversation_to_text(s.data["ids"][0])
            filename = f"{Message.get_first_msg(s.data['ids'][0]).send_time.strftime('%Y-%m-%d_%H-%M-%S')}.txt"
            content_type = 'text/plain'
        else:
            zip_content = BytesIO()
            with ZipFile(zip_content, 'w') as _zip:
                for _id in s.data["ids"]:
                    _content = Message.conversation_to_text(_id)
                    _zip.writestr(Message.get_first_msg(_id).send_time.strftime('%Y-%m-%d_%H-%M-%S') + ".txt", _content)

            filename = f"{Message.get_first_msg(s.data['ids'][0]).send_time.strftime('%Y-%m-%d_%H-%M-%S')}.zip"
            content_type = 'application/x-zip-compressed'
            content = zip_content.getvalue()

        response = HttpResponse(content, content_type=content_type)
        response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
        response['Access-Control-Expose-Headers'] = 'Content-Disposition'
        return response


class VoteCreateAPIView(CreateAPIView, UpdateAPIView):
    serializer_class = VoteSerializer
    queryset = Vote.objects.all()


class TransmitterAPIView(CreateAPIView, UpdateAPIView):
    def get(self, request):
        return JsonResponse(
            list(Message.objects.filter(
                transmitter__type=AgentType.human.value
            ).values(
                "transmitter__id"
            ).distinct()),
            safe=False
        )
