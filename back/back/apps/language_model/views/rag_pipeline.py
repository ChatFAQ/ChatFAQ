from rest_framework import viewsets

from back.apps.language_model.models.rag_pipeline import LLMConfig, RAGConfig, GenerationConfig, PromptConfig, RetrieverConfig
from back.apps.language_model.serializers.rag_pipeline import LLMConfigSerializer, RAGConfigSerializer, \
    GenerationConfigSerializer, PromptConfigSerializer, RetrieverConfigSerializer


class RAGConfigAPIViewSet(viewsets.ModelViewSet):
    queryset = RAGConfig.objects.all()
    serializer_class = RAGConfigSerializer

    def get_queryset(self):
        if self.kwargs.get("pk"):
            kb = RAGConfig.objects.filter(name=self.kwargs["pk"]).first()
            if kb:
                self.kwargs["pk"] = str(kb.pk)
        return super().get_queryset()


class LLMConfigAPIViewSet(viewsets.ModelViewSet):
    queryset = LLMConfig.objects.all()
    serializer_class = LLMConfigSerializer


class RetrieverConfigAPIViewSet(viewsets.ModelViewSet):
    queryset = RetrieverConfig.objects.all()
    serializer_class = RetrieverConfigSerializer


class GenerationConfigAPIViewSet(viewsets.ModelViewSet):
    queryset = GenerationConfig.objects.all()
    serializer_class = GenerationConfigSerializer


class PromptConfigAPIViewSet(viewsets.ModelViewSet):
    queryset = PromptConfig.objects.all()
    serializer_class = PromptConfigSerializer
