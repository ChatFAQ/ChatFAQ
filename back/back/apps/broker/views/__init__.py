from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.views import APIView

from ..models.message import Message
from ..serializers.messages import MessageSerializer


class MessageView(LoginRequiredMixin, viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


class ConversationView(APIView):
    def get(self, request):
        return JsonResponse(Message.conversations_by_transmitter_id(request.GET["identifier"]), safe=False)


class ConversationInfoView(APIView):
    def get(self, request):
        return JsonResponse(Message.conversations_info_by_transmitter_id(request.GET["identifier"]), safe=False)
