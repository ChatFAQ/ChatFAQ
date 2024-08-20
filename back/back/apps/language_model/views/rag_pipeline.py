from rest_framework import viewsets
from django.http import JsonResponse
from rest_framework.decorators import action

from back.apps.language_model.models.rag_pipeline import LLMConfig, GenerationConfig, PromptConfig, RetrieverConfig
from back.apps.language_model.serializers.rag_pipeline import LLMConfigSerializer, \
    GenerationConfigSerializer, PromptConfigSerializer, RetrieverConfigSerializer
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.response import Response


class LLMConfigAPIViewSet(viewsets.ModelViewSet):
    queryset = LLMConfig.objects.all()
    serializer_class = LLMConfigSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["id"]
    search_fields = ['name']


class RetrieverConfigAPIViewSet(viewsets.ModelViewSet):
    queryset = RetrieverConfig.objects.all()
    serializer_class = RetrieverConfigSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["id"]
    search_fields = ['name']

    @action(detail=True, url_name='retrieve', url_path='retrieve', methods=['POST'], parser_classes=[JSONParser])
    def retrieve_knowledge_items(self, request, *args, **kwargs):
        """
        Retrieves Knowledge Items based on multiple query embeddings for a specific Retriever.
        """
        retriever_config = RetrieverConfig.objects.filter(pk=kwargs.get("pk")).first()
        query_embeddings_data = request.data.get('query_embeddings')  # Expecting a list of embeddings
        threshold = request.data.get('threshold', 0.0)
        top_k = request.data.get('top_k')

        if None in (query_embeddings_data, threshold, top_k) or not isinstance(query_embeddings_data, list):
            return Response({"error": "Invalid or missing required parameters."}, status=status.HTTP_400_BAD_REQUEST)

        all_items = []
        for query_embedding in query_embeddings_data:
            items = retriever_config.retrieve_kitems(query_embedding, threshold, top_k)
            all_items.extend(items)

        # Return serialized data
        return JsonResponse(all_items, safe=False)


class GenerationConfigAPIViewSet(viewsets.ModelViewSet):
    queryset = GenerationConfig.objects.all()
    serializer_class = GenerationConfigSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["id"]
    search_fields = ['name']


class PromptConfigAPIViewSet(viewsets.ModelViewSet):
    queryset = PromptConfig.objects.all()
    serializer_class = PromptConfigSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["id"]
    search_fields = ['name']
