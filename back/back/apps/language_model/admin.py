from django.contrib import admin

from .models import Dataset, Item, Utterance, Model

admin.site.register(Dataset)
admin.site.register(Item)
admin.site.register(Utterance)
admin.site.register(Model)
