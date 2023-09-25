from rest_framework import serializers

from back.apps.language_model.models.rag_pipeline import RAGConfig, LLMConfig, GenerationConfig, PromptConfig


class RAGConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = RAGConfig
        fields = "__all__"


class LLMConfigSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)

    class Meta:
        model = LLMConfig
        fields = "__all__"


class GenerationConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenerationConfig
        fields = "__all__"


class PromptConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromptConfig
        fields = "__all__"
