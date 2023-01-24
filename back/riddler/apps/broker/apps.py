from logging import getLogger
from django.apps import AppConfig
from riddler.utils import is_migrating

logger = getLogger(__name__)


class BrokerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "riddler.apps.broker"

    def ready(self):
        if is_migrating():
            return
        from riddler.apps.broker.consumers import bots
        from riddler.common.abs.bot_consumers import BrokerMetaClass
        for pc in BrokerMetaClass.registry:
            pc.register()
