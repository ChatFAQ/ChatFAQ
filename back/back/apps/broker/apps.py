import os
from logging import getLogger

from django.apps import AppConfig

from back.utils import is_migrating, is_celery_worker

logger = getLogger(__name__)


class BrokerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "back.apps.broker"

    def ready(self):
        if is_migrating():
            return

        from back.apps.broker.consumers import bots  # noqa  ## This is needed to self register the bots in the BrokerMetaClass
        from back.common.abs.bot_consumers import BrokerMetaClass
        from back.apps.broker.models import ConsumerRoundRobinQueue, RemoteSDKParsers

        for pc in BrokerMetaClass.registry:
            pc.register()

        if not (os.getenv("BUILD_MODE") in ["yes", "true"]) and not is_celery_worker():
            try:
                ConsumerRoundRobinQueue.clear()
            except Exception as e:
                logger.warning(f"Could not clear the round robin queue: {e}")
            try:
                RemoteSDKParsers.clear()
            except Exception as e:
                logger.warning(f"Could not clear the remote SDK parsers: {e}")
