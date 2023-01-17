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
        from riddler.apps.broker.models.platform_config import PlatformConfigMetaClass

        for pc_class in PlatformConfigMetaClass.registry:
            for pc in pc_class.get_queryset().all():
                pc.register()
