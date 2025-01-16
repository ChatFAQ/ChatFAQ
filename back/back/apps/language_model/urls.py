from rest_framework.routers import DefaultRouter
from django.urls import path

import back.apps.language_model.views.data
import back.apps.language_model.views.rag_pipeline
import back.apps.language_model.views.tasks

router = DefaultRouter()
router.register(r"knowledge-bases", back.apps.language_model.views.data.KnowledgeBaseAPIViewSet, basename="knowledge-base")
router.register(r"data-sources", back.apps.language_model.views.data.DataSourceAPIViewSet, basename="data-source")
router.register(r"knowledge-items", back.apps.language_model.views.data.KnowledgeItemAPIViewSet, basename="knowledge-item")
router.register(r"knowledge-item-images", back.apps.language_model.views.data.KnowledgeItemImageAPIViewSet, basename="knowledge-item-image")
router.register(r"auto-generated-titles", back.apps.language_model.views.data.AutoGeneratedTitleAPIViewSet, basename="auto-generated-title")
router.register(r"llm-configs", back.apps.language_model.views.rag_pipeline.LLMConfigAPIViewSet, basename="llm-config")
router.register(r"retriever-configs", back.apps.language_model.views.rag_pipeline.RetrieverConfigAPIViewSet, basename="retriever-config")
router.register(r"generation-configs", back.apps.language_model.views.rag_pipeline.GenerationConfigAPIViewSet, basename="generation-config")
router.register(r"prompt-configs", back.apps.language_model.views.rag_pipeline.PromptConfigAPIViewSet, basename="prompt-config")
router.register(r"intents", back.apps.language_model.views.data.IntentAPIViewSet, basename="intent")

urlpatterns = router.urls

urlpatterns += [
    path("tasks/", back.apps.language_model.views.tasks.ListTasksAPI.as_view()),
    path("ray-status/", back.apps.language_model.views.tasks.RayStatusAPI.as_view()),
]
