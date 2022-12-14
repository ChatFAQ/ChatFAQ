from logging import getLogger
from urllib.parse import urljoin

import requests
from django.apps import AppConfig
from django.urls import reverse

from riddler.config import settings

logger = getLogger(__name__)


class BrokerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "riddler.apps.broker"

    def ready(self):

        if settings.TG_TOKEN:
            webhookUrl = urljoin(settings.BASE_URL, reverse("webhooks_telegram"))
            logger.debug(f"Notifying to Telegram our WebHook Url: {webhookUrl}")
            res = requests.get(
                f"{settings.TG_BOT_API_URL}{settings.TG_TOKEN}/setWebhook",
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
