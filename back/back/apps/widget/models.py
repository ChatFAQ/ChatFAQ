from django.db import models
from django.db.models import JSONField
from uuid import uuid4

from simple_history.models import HistoricalRecords

from back.apps.widget.constants import THEME_DEFAULTS


class Theme(models.Model):
    name = models.CharField(max_length=255)
    data = JSONField(default=THEME_DEFAULTS)

    history = HistoricalRecords()


class Widget(models.Model):
    id = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid4,
    )
    name = models.CharField(max_length=255)
    domain = models.URLField()
    fsm_def = models.CharField(max_length=255)
    title = models.CharField(max_length=255, null=True, blank=True)
    subtitle = models.CharField(max_length=255, null=True, blank=True)
    fullScreen = models.BooleanField(default=False)
    maximized = models.BooleanField(default=False)
    history_opened = models.BooleanField(default=False)
    theme = models.ForeignKey(Theme, on_delete=models.SET_NULL, null=True)
    manage_user_id = models.BooleanField(default=True)
    display_generation = models.BooleanField(default=True)
    display_sources = models.BooleanField(default=True)
    sources_first = models.BooleanField(default=False)

    history = HistoricalRecords()
