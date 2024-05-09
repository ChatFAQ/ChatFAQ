from django.http import JsonResponse
from back.apps.language_model.serializers.tasks import RayTaskSerializer
from rest_framework.views import APIView
from ray.util.state import api as ray_api
from drf_spectacular.utils import extend_schema


class ListTasksAPI(APIView):
    @extend_schema(responses={200: RayTaskSerializer(many=True)})
    def get(self, request):
        """
        Return a list of all ray tasks.
        """
        return JsonResponse([j.__dict__ for j in ray_api.list_tasks()], safe=False)
