from django.contrib import admin
from django.db.models import Q
from django.contrib import messages

from .forms import PromptConfigForm
from .tasks import index_task
from simple_history.admin import SimpleHistoryAdmin

from .models.data import (
    KnowledgeBase,
    KnowledgeItem,
    Embedding,
    AutoGeneratedTitle,
    Intent,
    MessageKnowledgeItem,
    delete_knowledge_items,
    KnowledgeItemImage,
)
from .models.rag_pipeline import (
    RAGConfig,
    LLMConfig,
    PromptConfig,
    GenerationConfig,
    RetrieverConfig,
)
from .forms import KnowledgeBaseForm


class PromptConfigAdmin(SimpleHistoryAdmin):
    form = PromptConfigForm


class KnowledgeItemAdmin(admin.ModelAdmin):
    list_display = ["content", "url"]
    list_filter = ["knowledge_base"]

    def delete_queryset(self, request, queryset):
        # Call your custom delete function
        knowledge_item_ids = queryset.values_list("id", flat=True)
        delete_knowledge_items(list(knowledge_item_ids))


class KnowledgeBaseAdmin(admin.ModelAdmin):
    form = KnowledgeBaseForm


class AutoGeneratedTitleAdmin(admin.ModelAdmin):
    list_display = ["knowledge_item_id", "title"]
    list_filter = ["knowledge_item__knowledge_base"]


# Custom filter for KnowledgeBase
class KnowledgeBaseFilter(admin.SimpleListFilter):
    title = "knowledge base"
    parameter_name = "knowledge_base"

    def lookups(self, request, model_admin):
        # Return a list of tuples. The first element in each tuple is the coded value
        # for the option that will appear in the URL query. The second element is the
        # human-readable name for the option that will appear in the right sidebar.
        knowledge_bases = KnowledgeBase.objects.all()
        return [(kb.id, kb.name) for kb in knowledge_bases]

    def queryset(self, request, queryset):
        # Filter the queryset based on the value provided in the query string.
        if self.value():
            return queryset.filter(
                Q(knowledge_item__knowledge_base=self.value())
                | Q(
                    message__messageknowledgeitem__knowledge_item__knowledge_base=self.value()
                )
            ).distinct()
        return queryset


class IntentAdmin(admin.ModelAdmin):
    list_display = ["intent_name", "suggested_intent", "auto_generated"]
    list_filter = ["suggested_intent", KnowledgeBaseFilter]


def run_index_task(modeladmin, request, queryset):
    for rag_config in queryset:
        index_task.delay(rag_config.id, recache_models=True, caller='RagConfig Admin')  # Trigger the Celery task
        modeladmin.message_user(request, f"Index task started for {rag_config.name}", messages.SUCCESS)

run_index_task.short_description = "Index selected RAG configs"

class RagConfigAdmin(admin.ModelAdmin):
    list_display = ["name", "disabled"]
    list_filter = ["disabled"]
    actions = [run_index_task]


admin.site.register(RAGConfig, RagConfigAdmin)
admin.site.register(KnowledgeBase, KnowledgeBaseAdmin)
admin.site.register(KnowledgeItem, KnowledgeItemAdmin)
admin.site.register(KnowledgeItemImage)
admin.site.register(AutoGeneratedTitle, AutoGeneratedTitleAdmin)
admin.site.register(LLMConfig)
admin.site.register(PromptConfig, PromptConfigAdmin)
admin.site.register(GenerationConfig)
admin.site.register(RetrieverConfig)
admin.site.register(Embedding)
admin.site.register(Intent, IntentAdmin)
admin.site.register(MessageKnowledgeItem)
