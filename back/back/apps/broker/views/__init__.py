from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.views import APIView

from ..models.message import Message
from ..serializers import ConversationSerializer, TransmitterSerializer, ConversationsSerializer
from ..serializers.messages import MessageSerializer


class MessageView(LoginRequiredMixin, viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


class ConversationView(APIView):
    def get(self, request):
        s = ConversationSerializer(data=request.GET)
        s.is_valid(raise_exception=True)
        return JsonResponse(
            Message.conversation_chain(s.data["id"]), safe=False
        )

    def delete(self, request):
        s = ConversationSerializer(data=request.GET)
        s.is_valid(raise_exception=True)
        Message.delete_conversation()


class ConversationsInfoView(APIView):
    def get(self, request):
        s = TransmitterSerializer(data=request.GET)
        s.is_valid(raise_exception=True)
        return JsonResponse(
            Message.conversations_info(s.data["id"]), safe=False
        )

    def delete(self, request):
        s = ConversationsSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        Message.delete_conversations(s.data["ids"])
        return JsonResponse({})
