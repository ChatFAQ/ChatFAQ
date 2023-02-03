from django.contrib.auth.mixins import LoginRequiredMixin
from .models import FSMDefinition
from .serializers import FSMSerializer
from ...common.views import DynamicFieldsView


class FSMView(DynamicFieldsView, LoginRequiredMixin):
    queryset = FSMDefinition.objects.all()
    serializer_class = FSMSerializer
