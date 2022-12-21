from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from rest_framework import viewsets

from riddler.apps.fsm.models import FiniteStateMachine

from ..models.message import Message
from ..models.platform_bot import PlatformBot
from ..serializers.message import MessageSerializer
from ..serializers.platform_bot import PlatformBotSerializer


# TODO: @extend_schema for message stacks[][].type <-> message stacks[][].payload
class MessageView(LoginRequiredMixin, viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


# TODO: @extend_schema for platform_types <-> platform_meta
class PlatformBotView(LoginRequiredMixin, viewsets.ModelViewSet):
    queryset = PlatformBot.objects.all()
    serializer_class = PlatformBotSerializer


def chat(request):
    fsm_names = list(FiniteStateMachine.objects.values_list("name", flat=True))
    return render(request, "chat/index.html", {"fsm_names": fsm_names})


def room(request, conversation, fsm):
    return render(request, "chat/room.html", {"conversation": conversation, "fsm": fsm})
