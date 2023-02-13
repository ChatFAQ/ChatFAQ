from logging import getLogger

from django.apps import AppConfig

from back.utils import is_migrating

logger = getLogger(__name__)


class BrokerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "back.apps.broker"

    def ready(self):
        if is_migrating():
            return
        from back.apps.broker.consumers import bots
        from back.common.abs.bot_consumers import BrokerMetaClass

        for pc in BrokerMetaClass.registry:
            pc.register()
