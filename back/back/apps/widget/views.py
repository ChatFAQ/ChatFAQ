from rest_framework import viewsets, filters, exceptions
from django.http import JsonResponse

from back.apps.widget.constants import THEME_DEFAULTS_BY_SECTION
from back.apps.widget.models import Widget, Theme
from back.apps.widget.serializers import WidgetSerializer, ThemeSerializer
from rest_framework.views import APIView

from django_filters.rest_framework.backends import DjangoFilterBackend

from rest_framework.filters import OrderingFilter, SearchFilter

from back.config.middelware import IsAuthenticatedOrWidgetOriginHostPermission


class WidgetAPIViewSet(viewsets.ModelViewSet):
    queryset = Widget.objects.all()
    serializer_class = WidgetSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["id"]
    permission_classes = [IsAuthenticatedOrWidgetOriginHostPermission]

    def check_object_permissions(self, request, obj):
        if obj.authentication_required:
            if not request.user.is_authenticated:
                raise exceptions.NotAuthenticated()
        return super().check_object_permissions(request, obj)


class ThemeAPIViewSet(viewsets.ModelViewSet):
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["id"]


# create ThemeDefaultsAPIViewSet generic apiview just with one method: get
class ThemeDefaultsAPIViewSet(APIView):
    def get(self, request):
        default = {}
        return JsonResponse(THEME_DEFAULTS_BY_SECTION)
