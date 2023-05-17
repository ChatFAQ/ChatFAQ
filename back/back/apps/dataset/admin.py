from django.contrib import admin
from .models import Dataset, Item, Utterance

admin.site.register(Dataset)
admin.site.register(Item)
admin.site.register(Utterance)
