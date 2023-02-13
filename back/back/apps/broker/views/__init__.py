from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from rest_framework import viewsets

from ...fsm.models import FSMDefinition
from ..models.message import Message
from ..serializers.messages import MessageSerializer


class MessageView(LoginRequiredMixin, viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
