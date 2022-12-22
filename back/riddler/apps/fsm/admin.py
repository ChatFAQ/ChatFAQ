from django.contrib import admin
from django.contrib.postgres.fields import ArrayField as DjangoArrayField
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin
from django_better_admin_arrayfield.forms.widgets import DynamicArrayTextareaWidget

from .models import CachedFSM, FSMDefinition


class FSMDefinitionAdmin(admin.ModelAdmin, DynamicArrayMixin):
    formfield_overrides = {
        DjangoArrayField: {"widget": DynamicArrayTextareaWidget},
    }


class CachedFSMAdmin(admin.ModelAdmin):
    pass


admin.site.register(FSMDefinition, FSMDefinitionAdmin)
admin.site.register(CachedFSM, CachedFSMAdmin)
