from enum import Enum

from django.db import models

from riddler.apps.fsm.models import FiniteStateMachine
from riddler.common.models import ChangesMixin


class PlatformTypes(Enum):
    telegram = "telegram"
    ws = "ws"


class PlatformBot(ChangesMixin):
    """
    This represents the association between a message platform and a FSM
    """
    fsm = models.ForeignKey(FiniteStateMachine, on_delete=models.CASCADE)
    platform_type = models.CharField(max_length=255, choices=((v.value, v.value) for v in PlatformTypes))
    platform_meta = models.JSONField(default=dict)

    def platform_view_name(self):
        if self.platform_type == PlatformTypes.telegram.value:
            return f"webhook_{self.platform_type}_{self.platform_meta['token'].replace(':', '_')}"
        else:
            raise "Platform not supported"
