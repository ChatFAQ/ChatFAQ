from rest_framework.routers import DefaultRouter

import back.apps.language_model.views.data
import back.apps.language_model.views.rag_pipeline

router = DefaultRouter()
router.register(r"knowledge-bases", back.apps.language_model.views.data.KnowledgeBaseAPIViewSet, basename="knowledge-base")
router.register(r"knowledge-items", back.apps.language_model.views.data.KnowledgeItemAPIViewSet, basename="item")
router.register(r"auto-generated-titles", back.apps.language_model.views.data.AutoGeneratedTitleAPIViewSet, basename="utterance")
router.register(r"llm-configs", back.apps.language_model.views.rag_pipeline.LLMConfigAPIViewSet, basename="llm-config")
router.register(r"rag-configs", back.apps.language_model.views.rag_pipeline.RAGConfigAPIViewSet, basename="rag-config")
router.register(r"retriever-configs", back.apps.language_model.views.rag_pipeline.RetrieverConfigAPIViewSet, basename="retriever-config")
router.register(r"generation-configs", back.apps.language_model.views.rag_pipeline.GenerationConfigAPIViewSet, basename="generation-config")
router.register(r"prompt-configs", back.apps.language_model.views.rag_pipeline.PromptConfigAPIViewSet, basename="prompt-config")

urlpatterns = router.urls
