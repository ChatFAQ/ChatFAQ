from django.contrib import admin
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin
from django.db.models import JSONField
from .models import CachedFSM, FSMDefinition
from ...utils import PrettyJSONWidget


class FSMDefinitionAdmin(admin.ModelAdmin, DynamicArrayMixin):
    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget}
    }


class CachedFSMAdmin(admin.ModelAdmin):
    pass


admin.site.register(FSMDefinition, FSMDefinitionAdmin)
admin.site.register(CachedFSM, CachedFSMAdmin)
