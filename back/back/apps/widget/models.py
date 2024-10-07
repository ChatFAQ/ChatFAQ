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
    # general
    id = models.UUIDField(
        primary_key=True,
        editable=False,
        default=uuid4,
    )
    name = models.CharField(max_length=255)
    domain = models.URLField()
    fsm_def = models.CharField(null=True, max_length=255)
    chatfaq_ws = models.URLField(null=True)
    chatfaq_api = models.URLField(null=True)
    lang = models.CharField(null=True, max_length=255)
    # look and feel
    title = models.CharField(max_length=255, null=True, blank=True)
    subtitle = models.CharField(max_length=255, null=True, blank=True)
    full_screen = models.BooleanField(default=False)
    only_chat = models.BooleanField(default=False)
    start_small_mode = models.BooleanField(default=False)
    start_with_history_closed = models.BooleanField(default=False)
    sources_first = models.BooleanField(default=False)
    stick_input_prompt = models.BooleanField(default=False)
    # integration
    fit_to_parent = models.BooleanField(default=False)
    # advanced
    custom_css = models.TextField(null=True, blank=True)
    initial_conversation_metadata = JSONField(default=dict)
    custom_i_dramed_msgs = JSONField(default=dict)
    # ----------
    history = HistoricalRecords()
