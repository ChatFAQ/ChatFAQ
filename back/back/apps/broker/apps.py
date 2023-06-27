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

        from back.common.abs.bot_consumers import BrokerMetaClass
        from back.apps.broker.models import RPCConsumerRoundRobinQueue

        for pc in BrokerMetaClass.registry:
            pc.register()

        RPCConsumerRoundRobinQueue.clear()
