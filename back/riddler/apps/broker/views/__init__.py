from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from rest_framework import viewsets

from ..models import Message
from ..serializers import MessageSerializer
from riddler.apps.fsm.models import FiniteStateMachine


class MessageView(LoginRequiredMixin, viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


def chat(request):
    fsm_names = list(FiniteStateMachine.objects.values_list("name", flat=True))
    return render(request, "chat/index.html", {"fsm_names": fsm_names})


def room(request, conversation, fsm):
    return render(request, "chat/room.html", {"conversation": conversation, "fsm": fsm})
