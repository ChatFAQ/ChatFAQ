from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from rest_framework import viewsets

from ..models.message import Message
from ..serializers.messages import MessageSerializer
from ...fsm.models import FSMDefinition


# TODO: @extend_schema for message stacks[][].type <-> message stacks[][].payload
class MessageView(LoginRequiredMixin, viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


def chat(request):
    fsm_def_ids = list(FSMDefinition.objects.values_list("pk", flat=True))
    return render(request, "chat/index.html", {"fsm_def_ids": fsm_def_ids})


def room(request, conversation, fsm_def_id):
    return render(request, "chat/room.html", {"conversation": conversation, "fsm_def_id": fsm_def_id})
