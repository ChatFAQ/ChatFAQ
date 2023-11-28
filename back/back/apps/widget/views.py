from rest_framework import viewsets
from django.http import JsonResponse

from back.apps.widget.constants import THEME_DEFAULTS
from back.apps.widget.models import Widget, Theme
from back.apps.widget.serializers import WidgetSerializer, ThemeSerializer
from rest_framework.views import APIView


class WidgetAPIViewSet(viewsets.ModelViewSet):
    queryset = Widget.objects.all()
    serializer_class = WidgetSerializer


class ThemeAPIViewSet(viewsets.ModelViewSet):
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer


# create ThemeDefaultsAPIViewSet generic apiview just with one method: get
class ThemeDefaultsAPIViewSet(APIView):
    def get(self, request):
        default = {}
        return JsonResponse(THEME_DEFAULTS)
