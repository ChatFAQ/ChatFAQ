from rest_framework import viewsets
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import FiniteStateMachine
from .serializers import FSMSerializer


class FSMView(LoginRequiredMixin, viewsets.ModelViewSet):
    queryset = FiniteStateMachine.objects.all()
    serializer_class = FSMSerializer
