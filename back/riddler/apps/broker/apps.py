from logging import getLogger
from urllib.parse import urljoin

import requests
from django.apps import AppConfig, apps
from django.urls import reverse

from riddler.config import settings

logger = getLogger(__name__)


class BrokerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "riddler.apps.broker"

    def ready(self):
        from .models.platform_bot import PlatformTypes
        PlatformBot = apps.get_model('broker', 'PlatformBot')

        for pb in PlatformBot.objects.all():
            if pb.platform_type == PlatformTypes.telegram.value:
                webhookUrl = urljoin(settings.BASE_URL, reverse(pb.platform_view_name()))
                logger.debug(f"Notifying to Telegram our WebHook Url: {webhookUrl}")
                res = requests.get(
                    f"{pb.platform_meta['api_url']}{pb.platform_meta['token']}/setWebhook",
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
