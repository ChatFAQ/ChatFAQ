from django_celery_results.models import TaskResult
from rest_framework import viewsets
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from back.apps.language_model.serializers.tasks import TaskResultSerializer


class TaskResultAPIViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        return TaskResult.objects.exclude(task_name__contains="llm_query_task")

    queryset = TaskResult.objects.all()
    serializer_class = TaskResultSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["id"]
