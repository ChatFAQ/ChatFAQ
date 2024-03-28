import os

from django.apps import AppConfig

from back.utils import is_migrating, is_celery_worker

from logging import getLogger

logger = getLogger(__name__)


class DatasetConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "back.apps.language_model"

    def ready(self):
        if is_migrating() or os.getenv("BUILD_MODE") in ["yes", "true"] or is_celery_worker():
            return
        from .signals import on_llm_config_change # noqa

