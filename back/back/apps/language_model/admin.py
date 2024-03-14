from django.contrib import admin
from django.db.models import Q
from django.contrib import messages

from .forms import PromptConfigForm
from simple_history.admin import SimpleHistoryAdmin

from .models.data import (
    KnowledgeBase,
    KnowledgeItem,
    Embedding,
    AutoGeneratedTitle,
    Intent,
    MessageKnowledgeItem,
    KnowledgeItemImage, DataSource,
)
from .models.rag_pipeline import (
    RAGConfig,
    LLMConfig,
    PromptConfig,
    GenerationConfig,
    RetrieverConfig,
)
from .forms import DataSourceForm


class PromptConfigAdmin(SimpleHistoryAdmin):
    form = PromptConfigForm


class KnowledgeItemAdmin(admin.ModelAdmin):
    list_display = ["content", "url"]
    list_filter = ["knowledge_base"]
    search_fields = ["title", "content", "url", "metadata"]


class KnowledgeItemImageAdmin(admin.ModelAdmin):
    search_fields = ["knowledge_item__title", "knowledge_item__content", "image_caption"]
    list_filter = ["knowledge_item__knowledge_base"]



class DataSourceAdmin(admin.ModelAdmin):
    form = DataSourceForm


class DataSourceInline(admin.TabularInline):
    model = DataSource
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class KnowledgeBaseAdmin(admin.ModelAdmin):
    model = KnowledgeBase
    inlines = [
        DataSourceInline,
    ]


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
        rag_config.trigger_reindex(True, 'RagConfig Django Admin')
        modeladmin.message_user(request, f"Index task started for {rag_config.name}", messages.SUCCESS)

run_index_task.short_description = "Index selected RAG configs"


class RagConfigAdmin(admin.ModelAdmin):
    list_display = ["name", "disabled", "index_up_to_date"]
    list_filter = ["disabled", "index_up_to_date"]
    actions = [run_index_task]

    def get_readonly_fields(self, request, obj=None):
        # This makes 'index_up_to_date' readonly in all cases
        return self.readonly_fields + ('index_up_to_date', 's3_index_path',)
    

class MessageKnowledgeItemAdmin(admin.ModelAdmin):
    list_display = ["message_id", "knowledge_item_id", "similarity", "valid"]
    list_filter = ["knowledge_item__knowledge_base"]
    ordering = ["message_id"]


admin.site.register(RAGConfig, RagConfigAdmin)
admin.site.register(KnowledgeBase, KnowledgeBaseAdmin)
admin.site.register(KnowledgeItem, KnowledgeItemAdmin)
admin.site.register(KnowledgeItemImage, KnowledgeItemImageAdmin)
admin.site.register(AutoGeneratedTitle, AutoGeneratedTitleAdmin)
admin.site.register(LLMConfig)
admin.site.register(PromptConfig, PromptConfigAdmin)
admin.site.register(GenerationConfig)
admin.site.register(RetrieverConfig)
admin.site.register(Embedding)
admin.site.register(DataSource, DataSourceAdmin)
admin.site.register(Intent, IntentAdmin)
admin.site.register(MessageKnowledgeItem, MessageKnowledgeItemAdmin)
