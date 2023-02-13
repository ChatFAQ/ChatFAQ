from django.contrib.auth.mixins import LoginRequiredMixin

from ...common.views import DynamicFieldsView
from .models import FSMDefinition
from .serializers import FSMSerializer


class FSMView(DynamicFieldsView, LoginRequiredMixin):
    queryset = FSMDefinition.objects.all()
    serializer_class = FSMSerializer
