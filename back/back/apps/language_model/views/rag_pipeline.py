from rest_framework import viewsets

from back.apps.language_model.models.rag_pipeline import LLMConfig, RAGConfig, GenerationConfig, PromptConfig, RetrieverConfig
from back.apps.language_model.serializers.rag_pipeline import LLMConfigSerializer, RAGConfigSerializer, \
    GenerationConfigSerializer, PromptConfigSerializer, RetrieverConfigSerializer


class LLMConfigAPIViewSet(viewsets.ModelViewSet):
    queryset = LLMConfig.objects.all()
    serializer_class = LLMConfigSerializer


class RAGConfigAPIViewSet(viewsets.ModelViewSet):
    queryset = RAGConfig.objects.all()
    serializer_class = RAGConfigSerializer


class RetrieverConfigAPIViewSet(viewsets.ModelViewSet):
    queryset = RetrieverConfig.objects.all()
    serializer_class = RetrieverConfigSerializer


class GenerationConfigAPIViewSet(viewsets.ModelViewSet):
    queryset = GenerationConfig.objects.all()
    serializer_class = GenerationConfigSerializer


class PromptConfigAPIViewSet(viewsets.ModelViewSet):
    queryset = PromptConfig.objects.all()
    serializer_class = PromptConfigSerializer
