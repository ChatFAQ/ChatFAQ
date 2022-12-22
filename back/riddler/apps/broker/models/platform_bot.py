from enum import Enum

from django.db import models

from riddler.apps.fsm.models import FSMDefinition
from riddler.common.models import ChangesMixin


class PlatformTypes(Enum):
    telegram = "telegram"
    ws = "ws"


class PlatformBot(ChangesMixin):
    """
    This represents the association between a message platform and a FSM
    Attributes
    ----------
    fsm_def
        A reference to the finite state machine model
    platform_type : str
        Telegram, Whatsapp, etc...
    platform_meta : dict
        metadata specific to the platform itself, they often are tokens, api_urls, etc...
    """
    fsm_def = models.ForeignKey(FSMDefinition, on_delete=models.CASCADE)
    platform_type = models.CharField(max_length=255, choices=((v.value, v.value) for v in PlatformTypes))
    platform_meta = models.JSONField(default=dict)

    def platform_view_name(self):
        """
        Just an utility function to control the url's view name depending on the platform type since this name will
        most likely depend on the metadata of the paltform
        """
        if self.platform_type == PlatformTypes.telegram.value:
            return f"webhook_{self.platform_type}_{self.platform_meta['token'].replace(':', '_')}"
        else:
            raise "Platform not supported"
