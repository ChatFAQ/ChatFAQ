from django_celery_results.models import TaskResult
from rest_framework import viewsets
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.http import JsonResponse
from rest_framework.decorators import action
from back.apps.language_model.serializers.tasks import TaskResultSerializer
from back.utils.ray_connection import ray_and_celery_tasks, get_ray_tasks
from back.apps.language_model.ray_tasks.ray_tasks import test_task


class TaskResultAPIViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TaskResult.objects.all()
    serializer_class = TaskResultSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["id"]

    @action(detail=False, methods=["get"])
    def get_all_tasks(self, request):
        return JsonResponse(ray_and_celery_tasks(), safe=False)

    @action(detail=False, methods=["get"])
    def get_ray_tasks(self, request):
        return JsonResponse(get_ray_tasks(), safe=False)

    @action(detail=False, methods=["get"])
    def launch_test_task(self, request):
        import uuid
        test_task.options(name="test_task").remote(str(uuid.uuid4()))
        return JsonResponse({"res": "ok"}, safe=False)
