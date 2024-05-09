from django.http import JsonResponse

from back.apps.language_model.models import RayTaskState
from back.apps.language_model.serializers.tasks import RayTaskStateSerializer
from rest_framework.views import APIView
from ray.util.state import api as ray_api
from drf_spectacular.utils import extend_schema


class ListTasksAPI(APIView):
    @extend_schema(responses={200: RayTaskStateSerializer(many=True)})
    def get(self, request):
        """
        Return a list of all ray tasks.
        """
        data = RayTaskState.get_all_ray_and_parse_tasks_serialized()

        return JsonResponse(data, safe=False)
