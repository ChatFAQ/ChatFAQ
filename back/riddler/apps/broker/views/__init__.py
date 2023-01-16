from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from rest_framework import viewsets

from ..models.message import Message
from ..models.platform_config import PlatformConfig, PlatformTypes
from ..serializers.message import MessageSerializer
from ..serializers.platform_config import PlatformConfigSerializer


# TODO: @extend_schema for message stacks[][].type <-> message stacks[][].payload
class MessageView(LoginRequiredMixin, viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


# TODO: @extend_schema for platform_types <-> platform_meta
class PlatformConfigView(LoginRequiredMixin, viewsets.ModelViewSet):
    queryset = PlatformConfig.objects.all()
    serializer_class = PlatformConfigSerializer


def chat(request):
    pc_ids = list(PlatformConfig.objects.filter(platform_type=PlatformTypes.ws.value).values_list("pk", flat=True))
    return render(request, "chat/index.html", {"pc_ids": pc_ids})


def room(request, conversation, pc_id):
    return render(request, "chat/room.html", {"conversation": conversation, "pc_id": pc_id})
