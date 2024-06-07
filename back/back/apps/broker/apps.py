import os
from logging import getLogger

from django.apps import AppConfig

from back.utils import is_server_process
import ray
logger = getLogger(__name__)


class BrokerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "back.apps.broker"

    def ready(self):
        if not is_server_process():
            return
        from back.apps.broker.consumers import bots  # noqa  ## This is needed to self register the bots in the BrokerMetaClass
        from back.common.abs.bot_consumers import BrokerMetaClass
        from back.apps.broker.models import ConsumerRoundRobinQueue, RemoteSDKParsers

        for pc in BrokerMetaClass.registry:
            pc.register()
        return

        try:
            ConsumerRoundRobinQueue.clear()
        except Exception as e:
            logger.warning(f"Could not clear the round robin queue: {e}")
        try:
            RemoteSDKParsers.clear()
        except Exception as e:
            logger.warning(f"Could not clear the remote SDK parsers: {e}")
