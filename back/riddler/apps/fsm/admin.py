from django.contrib import admin
from django.contrib.postgres.fields import ArrayField as DjangoArrayField
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin
from django_better_admin_arrayfield.forms.widgets import DynamicArrayTextareaWidget

from .models import CachedMachine, FSMDefinition


class FSMDefinitionAdmin(admin.ModelAdmin, DynamicArrayMixin):
    formfield_overrides = {
        DjangoArrayField: {"widget": DynamicArrayTextareaWidget},
    }


class CachedMachineAdmin(admin.ModelAdmin):
    pass


admin.site.register(FSMDefinition, FSMDefinitionAdmin)
admin.site.register(CachedMachine, CachedMachineAdmin)
