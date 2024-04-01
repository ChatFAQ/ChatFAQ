from rest_framework import viewsets, filters
from django.http import JsonResponse
from rest_framework.decorators import action
from back.apps.language_model.models.rag_pipeline import LLMConfig, RAGConfig, GenerationConfig, PromptConfig, RetrieverConfig
from back.apps.language_model.serializers.rag_pipeline import LLMConfigSerializer, RAGConfigSerializer, \
    GenerationConfigSerializer, PromptConfigSerializer, RetrieverConfigSerializer
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


class RAGConfigAPIViewSet(viewsets.ModelViewSet):
    queryset = RAGConfig.objects.all()
    serializer_class = RAGConfigSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["id", "disabled"]
    search_fields = ['name']


    def get_queryset(self):
        if self.kwargs.get("pk"):
            kb = RAGConfig.objects.filter(name=self.kwargs["pk"]).first()
            if kb:
                self.kwargs["pk"] = str(kb.pk)
        return super().get_queryset()

    @action(detail=True, url_name="trigger-reindex", url_path="trigger-reindex")
    def trigger_reindex(self, request, *args, **kwargs):
        """
        A view to trigger reindexing of the knowledge base:
        """
        rag_conf = RAGConfig.objects.filter(pk=kwargs["pk"]).first()
        if not rag_conf:
            return JsonResponse({"status": "knowledge base not found"}, status=404)
        rag_conf.trigger_reindex()
        return JsonResponse({"status": "reindex triggered"})


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
