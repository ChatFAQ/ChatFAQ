from logging import getLogger
from typing import Type

import requests
from django.conf import settings
from urllib.parse import urljoin

from enum import Enum

from django.db import models

from riddler.apps.broker.consumers.bot_examples.telegram import TelegramBotConsumer
from riddler.common.abs.bot_consumers.http import HTTPBotConsumer
from riddler.common.models import ChangesMixin

logger = getLogger()


class PlatformTypes(Enum):
    telegram = "telegram"
    ws = "ws"


class PlatformConfig(ChangesMixin):
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
    fsm_def = models.ForeignKey("fsm.FSMDefinition", on_delete=models.CASCADE)
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

    def platform_url_path(self) -> str:
        """
        Just an utility function to control the url's view depending on the platform type since this name will
        most likely depend on the metadata of the paltform
        """
        if self.platform_type == PlatformTypes.telegram.value:
            return f"back/webhooks/broker/telegram/{self.platform_meta['token']}"
        else:
            raise "Platform not supported"

    def platform_http_consumer(self) -> Type[HTTPBotConsumer]:
        """
        Just an utility function to control the url's view depending on the platform type since this name will
        most likely depend on the metadata of the paltform
        """
        if self.platform_type == PlatformTypes.telegram.value:
            return TelegramBotConsumer
        else:
            raise "Platform not supported"

    def register(self):
        if self.platform_type == PlatformTypes.telegram.value:
            webhookUrl = urljoin(settings.BASE_URL, self.platform_url_path())
            logger.debug(f"Notifying to Telegram our WebHook Url: {webhookUrl}")
            res = requests.get(
                f"{self.platform_meta['api_url']}{self.platform_meta['token']}/setWebhook",
                params={"url": webhookUrl},
            )
            if res.ok:
                logger.debug(
                    f"Successfully notified  WebhookUrl ({webhookUrl}) to Telegram"
                )
            else:
                logger.error(
                    f"Error notifying  WebhookUrl ({webhookUrl}) to Telegram: {res.text}"
                )
        else:
            pass


# TODO: Creating instances of Django proxy models from their base class
# so we can implement "platform_view_name", "platform_url_path", "platform_http_consumer" & "register" separately

'''
class TelegramPlatformConfig(PlatformConfig):
    """
    Telegram configuration
    """
    class Meta:
        proxy = True

    class TelegramPlatformConfigManager(models.Manager):
        def get_queryset(self):
            return super(
                TelegramPlatformConfig.TelegramPlatformConfigManager,
                self
            ).get_queryset().filter(platform_type=PlatformTypes.telegram.value)

    objects = TelegramPlatformConfigManager()
'''
