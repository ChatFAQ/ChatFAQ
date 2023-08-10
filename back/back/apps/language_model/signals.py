from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

from back.apps.language_model.models import Model, Dataset
from back.apps.language_model.tasks import recache_models


@receiver(post_save, sender=Model)
@receiver(post_delete, sender=Model)
@receiver(post_save, sender=Dataset)
@receiver(post_delete, sender=Dataset)
def on_model_or_dataset_change(instance, *args, **kwargs):
    recache_models.delay()


@receiver(pre_save, sender=Dataset)
def on_change(sender, instance: Dataset, **kwargs):
    if instance.id is not None:
        previous = Dataset.objects.get(id=instance.id)
        if previous.original_file != instance.original_file:
            instance.update_items_from_file()
