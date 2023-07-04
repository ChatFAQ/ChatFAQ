from django.contrib import admin

from .models import Dataset, Item, Utterance, Model, PromptStructure, GenerationConfig

admin.site.register(Dataset)
admin.site.register(Item)
admin.site.register(Utterance)
admin.site.register(Model)
admin.site.register(PromptStructure)
admin.site.register(GenerationConfig)
