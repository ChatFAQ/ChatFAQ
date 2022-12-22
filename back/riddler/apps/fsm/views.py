from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import viewsets

from .models import FSMDefinition
from .serializers import FSMSerializer


class FSMView(LoginRequiredMixin, viewsets.ModelViewSet):
    queryset = FSMDefinition.objects.all()
    serializer_class = FSMSerializer
