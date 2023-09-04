from django.contrib import admin

from .forms import PromptStructureForm
from .models import Dataset, Item, Utterance, Model, PromptStructure, GenerationConfig
from simple_history.admin import SimpleHistoryAdmin


class PromptStructureAdmin(SimpleHistoryAdmin):
    form = PromptStructureForm


class ItemAdmin(admin.ModelAdmin):
    list_display = ["answer", "url"]
    list_filter = ["dataset"]


admin.site.register(Dataset)
admin.site.register(Item, ItemAdmin)
admin.site.register(Utterance)
admin.site.register(Model)
admin.site.register(PromptStructure, PromptStructureAdmin)
admin.site.register(GenerationConfig)
