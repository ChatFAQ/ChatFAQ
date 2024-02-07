from rest_framework import serializers

from back.apps.language_model.models import KnowledgeBase
from back.apps.language_model.models.rag_pipeline import RAGConfig, LLMConfig, GenerationConfig, PromptConfig, RetrieverConfig


class RAGConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = RAGConfig
        fields = "__all__"

    def to_internal_value(self, data):
        if "knowledge_base" in data:
            kb = KnowledgeBase.objects.filter(name=data["knowledge_base"]).first()
            if kb:
                data["knowledge_base"] = str(kb.pk)
        if "llm_config" in data:
            llm_config = LLMConfig.objects.filter(name=data["llm_config"]).first()
            if llm_config:
                data["llm_config"] = str(llm_config.pk)
        if "prompt_config" in data:
            prompt_config = PromptConfig.objects.filter(name=data["prompt_config"]).first()
            if prompt_config:
                data["prompt_config"] = str(prompt_config.pk)
        if "generation_config" in data:
            generation_config = GenerationConfig.objects.filter(name=data["generation_config"]).first()
            if generation_config:
                data["generation_config"] = str(generation_config.pk)
        if "retriever_config" in data:
            retriever_config = RetrieverConfig.objects.filter(name=data["retriever_config"]).first()
            if retriever_config:
                data["retriever_config"] = str(retriever_config.pk)

        return super().to_internal_value(data)


class LLMConfigSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)

    class Meta:
        model = LLMConfig
        fields = "__all__"


class RetrieverConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = RetrieverConfig
        fields = "__all__"


class GenerationConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenerationConfig
        fields = "__all__"


class PromptConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromptConfig
        fields = "__all__"
