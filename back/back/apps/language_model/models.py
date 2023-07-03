from django.contrib.postgres.fields import ArrayField
from django.db import models

from back.common.models import ChangesMixin

from fernet_fields import EncryptedCharField


class Dataset(models.Model):
    """
    A dataset groups all its items under one language and keeps the original file for reference.

    name: str
        Just a name for the dataset.
    original_file: File
        The original file used to create the dataset.
    lang: en, es, fr
        The language of the dataset.
    """

    LANGUAGE_CHOICES = (
        ("en", "English"),
        ("es", "Spanish"),
        ("fr", "French"),
    )
    name = models.CharField(max_length=100)
    original_file = models.FileField()
    lang = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default="en")


class Item(ChangesMixin):
    """
    An item is a question/answer pair.

    dataset: Dataset
        The dataset it belongs to.
    intent: str
        The question of the FAQ.
    answer: str
        The answer to the FAQ.
    context: str
        The context of the FAQ, usually is the breadcrumb of the page where the FAQ is.
    role: str
        Sometimes the web pages have different user roles and it serves different FAQs to each one of them.
    url: str
        The URL of the page where the FAQ is.
    embedding: VectorField
        A computed embedding for the model.
    """

    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    intent = models.TextField()
    answer = models.TextField()
    url = models.URLField()
    context = models.TextField()
    role = models.CharField(max_length=255, blank=True, null=True)
    embedding = ArrayField(models.FloatField(), blank=True, null=True)


class Utterance(models.Model):
    """
    An utterance is a synonym of an item.

    item: Item
        The item this synonym refers to.
    intent: str
        The synonym of the item.
    embedding: VectorField
        A computed embedding for the model.
    """

    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    intent = models.TextField()
    embedding = ArrayField(models.FloatField(), blank=True, null=True)


class Model(models.Model):
    """
    A model is a dataset associated with a base model, trained or not.
    """

    STATUS_CHOICES = (
        ("created", "Created"),
        ("training", "Training"),
        ("trained", "Trained"),
    )

    name = models.CharField(max_length=100)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    repo_id = models.CharField(max_length=100, default="google/flan-t5-base")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="created")
    ggml_model_filename = models.CharField(max_length=255, blank=True, null=True)
    model_config = models.CharField(max_length=255, blank=True, null=True)
    hugginface_auth_token = EncryptedCharField(max_length=255, blank=True, null=True)
    load_in_8bit = models.BooleanField(default=False)
    trust_remote_code_tokenizer = models.BooleanField(default=False)
    trust_remote_code_model = models.BooleanField(default=False)
    revision = models.CharField(max_length=255, blank=True, null=True)

