from django_celery_results.models import TaskResult
from rest_framework import viewsets

from back.apps.language_model.serializers.tasks import TaskResultSerializer


class TaskResultAPIViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        return TaskResult.objects.exclude(task_name__contains="llm_query_task")

    queryset = TaskResult.objects.all()
    serializer_class = TaskResultSerializer
