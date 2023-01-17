from logging import getLogger
from typing import Type

import requests
from django.conf import settings
from urllib.parse import urljoin

from enum import Enum

from django.db import models
from django.db.models.base import ModelBase
from django.urls import re_path

from riddler.apps.broker.consumers.bot_examples.custom_ws import CustomWSBotConsumer
from riddler.apps.broker.consumers.bot_examples.telegram import TelegramBotConsumer
from riddler.common.abs.bot_consumers.http import BotConsumer, HTTPBotConsumer
from riddler.common.abs.bot_consumers.ws import WSBotConsumer
from riddler.common.models import ChangesMixin

logger = getLogger()


class PlatformTypes(Enum):
    telegram = "telegram"
    ws = "ws"


class PlatformConfigMetaClass(ModelBase):
    registry = []

    def __new__(cls, cls_name, bases, attrs):
        new_class = super().__new__(cls, cls_name, bases, attrs)
        if cls_name != "PlatformConfig":
            cls.registry.append(new_class)
        return new_class


class PlatformConfig(ChangesMixin, metaclass=PlatformConfigMetaClass):
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

    def get_queryset(self):
        """
        This method should filter the set of this platforms exclusivelly from any other platform, most likely by its platform_type
        """
        raise NotImplementedError

    @property
    def platform_url_path(self) -> str:
        """
        For controlling the view's url depending on the platform type since this name will
        most likely depend on the metadata of the platform
        """
        raise NotImplementedError

    @property
    def platform_consumer(self) -> Type[BotConsumer]:
        """
        The HTTP/WS consumer associated with the config
        """
        raise NotImplementedError

    def build_path(self):
        return re_path(
            self.platform_url_path,
            self.platform_consumer.as_asgi()
        )

    @property
    def is_http(self):
        return issubclass(self.platform_consumer, HTTPBotConsumer)

    @property
    def is_ws(self):
        return issubclass(self.platform_consumer, WSBotConsumer)

    def register(self):
        raise NotImplementedError


class TelegramPlatformConfig(PlatformConfig):
    """
    Telegram configuration
    """

    class Meta:
        proxy = True

    @classmethod
    def get_queryset(cls):
        return cls.objects.filter(platform_type=PlatformTypes.telegram.value)

    @property
    def platform_url_path(self) -> str:
        return f"back/webhooks/broker/telegram/{self.platform_meta['token']}"

    @property
    def platform_consumer(self) -> Type[BotConsumer]:
        return TelegramBotConsumer

    def register(self):
        webhookUrl = urljoin(settings.BASE_URL, self.platform_url_path)
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


class CustomWSPlatformConfig(PlatformConfig):
    """
    Custom WS configuration
    """

    class Meta:
        proxy = True

    @classmethod
    def get_queryset(cls):
        return cls.objects.filter(platform_type=PlatformTypes.ws.value)

    @property
    def platform_url_path(self) -> str:
        return r"back/ws/broker/(?P<conversation>\w+)/(?P<pc_id>\w+)/$"

    @property
    def platform_consumer(self) -> Type[BotConsumer]:
        return CustomWSBotConsumer

    def register(self):
        pass
