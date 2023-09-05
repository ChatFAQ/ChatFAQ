from django.contrib import admin

from .forms import PromptConfigForm
from .models import Dataset, Item, Utterance, LLMConfig, PromptConfig, GenerationConfig
from simple_history.admin import SimpleHistoryAdmin


class PromptConfigAdmin(SimpleHistoryAdmin):
    form = PromptConfigForm


class ItemAdmin(admin.ModelAdmin):
    list_display = ["answer", "url"]
    list_filter = ["dataset"]


admin.site.register(Dataset)
admin.site.register(Item, ItemAdmin)
admin.site.register(Utterance)
admin.site.register(LLMConfig)
admin.site.register(PromptConfig, PromptConfigAdmin)
admin.site.register(GenerationConfig)
