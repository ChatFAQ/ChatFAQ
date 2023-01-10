from logging import getLogger
from django.apps import AppConfig, apps
from riddler.utils import is_migrating

logger = getLogger(__name__)


class BrokerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "riddler.apps.broker"

    def ready(self):
        PlatformConfig = apps.get_model('broker', 'PlatformConfig')

        if is_migrating():
            return

        for pc in PlatformConfig.objects.all():
            pc.register()
