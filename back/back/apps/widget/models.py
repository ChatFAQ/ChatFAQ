from django.db import models
from django.db.models import JSONField

from back.apps.widget.constants import THEME_DEFAULTS


class Theme(models.Model):
    name = models.CharField(max_length=255)
    data = JSONField(default=THEME_DEFAULTS)


class Widget(models.Model):
    LAYOUT_CHOICES = (
        ("regular", "Regular"),
        ("full", "Full screen"),
    )
    # General
    name = models.CharField(max_length=255)
    domain = models.URLField()
    fsm_name = models.CharField(max_length=255)
    # Layout
    size = models.CharField(choices=LAYOUT_CHOICES, max_length=255, default=LAYOUT_CHOICES[0][0])
    history_opened = models.BooleanField(default=False)
    title = models.CharField(max_length=255, null=True, blank=True)
    subtitle = models.CharField(max_length=255, null=True, blank=True)
    theme = models.ForeignKey(Theme, on_delete=models.SET_NULL, null=True)
