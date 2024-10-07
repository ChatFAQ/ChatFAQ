from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import (
    Widget,
    Theme
)

admin.site.register(Theme, SimpleHistoryAdmin)
admin.site.register(Widget, SimpleHistoryAdmin)
