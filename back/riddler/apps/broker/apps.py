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
        from .models.platform_config import PlatformTypes
        PlatformConfig = apps.get_model('broker', 'PlatformConfig')

        for pc in PlatformConfig.objects.all():
            if pc.platform_type == PlatformTypes.telegram.value:
                webhookUrl = urljoin(settings.BASE_URL, reverse(pc.platform_view_name()))
                logger.debug(f"Notifying to Telegram our WebHook Url: {webhookUrl}")
                res = requests.get(
                    f"{pc.platform_meta['api_url']}{pc.platform_meta['token']}/setWebhook",
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
