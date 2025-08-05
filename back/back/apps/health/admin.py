from back.apps.health.models import Event
from django.contrib import admin


class EventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'is_success', 'date_created')
    list_filter = ('event_type', 'is_success')

admin.site.register(Event, EventAdmin)