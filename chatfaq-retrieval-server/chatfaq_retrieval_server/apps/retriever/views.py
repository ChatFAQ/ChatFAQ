
from rest_framework.views import APIView
from rest_framework.response import Response
from chatfaq_retrieval_server.apps.retriever.serializers import QuerySerializer
from logging import getLogger
from chatfaq_retrieval_server.utils import get_model

logger = getLogger(__name__)

# Create your views here.


class RetrieveAPIView(APIView):

    def get(self, request):
        serializer = QuerySerializer(request.data, many=True)
        serializer.is_valid(raise_exception=True)
        model = get_model(serializer.data["model_id"], request)
        res = model.query(serializer.data["query"])
        return Response(res)
