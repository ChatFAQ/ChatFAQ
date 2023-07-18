from django.contrib import admin

from .forms import PromptStructureForm
from .models import Dataset, Item, Utterance, Model, PromptStructure, GenerationConfig


class PromptStructureAdmin(admin.ModelAdmin):
    form = PromptStructureForm


admin.site.register(Dataset)
admin.site.register(Item)
admin.site.register(Utterance)
admin.site.register(Model)
admin.site.register(PromptStructure, PromptStructureAdmin)
admin.site.register(GenerationConfig)
