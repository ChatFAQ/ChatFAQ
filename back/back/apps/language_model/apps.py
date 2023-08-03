from django.apps import AppConfig


class DatasetConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "back.apps.language_model"

    def ready(self):
        from .signals import on_model_or_dataset_change # noqa
