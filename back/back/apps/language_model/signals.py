from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from back.apps.language_model.models import Model
from back.apps.language_model.tasks import recache_models


@receiver(post_save, sender=Model)
@receiver(post_delete, sender=Model)
def on_model_or_dataset_change(instance, *args, **kwargs):
    recache_models.delay()
