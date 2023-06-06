import json

from django.http import JsonResponse
from rest_framework.views import APIView
from chatfaq_retrieval_server.apps.retriever.serializers import QuerySerializer
from logging import getLogger
from chatfaq_retrieval_server.utils import get_model

logger = getLogger(__name__)

# Create your views here.


class RetrieveAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        serializer = QuerySerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        model = get_model(serializer.data["model_id"])
        res = model.query(serializer.data["query"])
        for c in res["context"]:
            c["role"] = None
        return JsonResponse(res, safe=False)

