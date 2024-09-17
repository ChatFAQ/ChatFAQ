from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from back.apps.language_model.models import RayTaskState
from back.apps.language_model.serializers.tasks import RayTaskStateSerializer
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema


def get_paginated_response(data, limit, offset, count):
    return JsonResponse({
        'limit': limit,
        'offset': offset,
        'count': count,
        'results': data
    }, safe=False)


class ListTasksAPI(APIView):
    @extend_schema(responses={200: RayTaskStateSerializer(many=True)})
    def get(self, request):
        """
        Return a list of all ray tasks.
        """
        # Get the request query params
        limit = request.query_params.get('limit')
        offset = request.query_params.get('offset')
        # Sorting
        sort_key = request.query_params.get('ordering', 'id')  # Default sort key
        task_id = request.query_params.get('task_id')  # Default sort order

        try:
            # Convert limit and offset to integers
            limit = int(limit) if limit is not None else None
            offset = int(offset) if offset is not None else None
        except ValueError:
            return Response({'error': 'Invalid limit or offset.'}, status=status.HTTP_400_BAD_REQUEST)

        data = RayTaskState.get_all_ray_and_parse_tasks_serialized()
        if sort_key:
            # if starts with "-" then sort in descending order
            sort_order = 'desc' if sort_key.startswith('-') else 'asc'
            if sort_order == 'desc':
                sort_key = sort_key[1:]
            if data and sort_key in data[0].keys():
                data = sorted(data, key=lambda x: x.get(sort_key), reverse=sort_order == 'desc')

        # Apply the pagination
        if limit and offset is not None:
            page = data[offset: offset + limit]
        else:
            page = data  # return all if limit or offset not provided
        # filter
        if task_id:
            page = [task for task in page if task.get('task_id') == task_id]

        return get_paginated_response(page, limit, offset, len(data))
