from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.views import APIView

from ..models.message import Message
from ..serializers import ConversationsSerializer, ConversationSerializer
from ..serializers.messages import MessageSerializer


class MessageView(LoginRequiredMixin, viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


class ConversationView(APIView):
    def get(self, request):
        s = ConversationSerializer(data=request.GET)
        s.is_valid(raise_exception=True)
        return JsonResponse(Message.conversation_chain(s.data["conversation_id"]), safe=False)


class ConversationsInfoView(APIView):
    def get(self, request):
        s = ConversationsSerializer(data=request.GET)
        s.is_valid(raise_exception=True)
        return JsonResponse(Message.conversations_info(s.data["transmitter_id"]), safe=False)
