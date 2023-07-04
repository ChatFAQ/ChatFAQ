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
    name: str
        Just a name for the model.
    dataset: Dataset
        The dataset it belongs to.
    repo_id: str
        The hugginface repo id of the base model.
    status: created, training, trained
        The status of the model.
    ggml_model_filename: str
        The GGML filename of the model.
    model_config: str
        The huggingface model config of the model.
    hugginface_auth_token: str
        The huggingface auth token to download from private repos.
    load_in_8bit: bool
        Whether to load the model in 8bit or not.
    trust_remote_code_tokenizer: bool
        Whether to trust the remote code for the tokenizer or not.
    trust_remote_code_model: bool
        Whether to trust the remote code for the model or not.
    revision: str
        The specific model version to use. It can be a branch name, a tag name, or a commit id, since we use a git-based system for storing models
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
    huggingface_auth_token = EncryptedCharField(max_length=255, blank=True, null=True)
    load_in_8bit = models.BooleanField(default=False)
    trust_remote_code_tokenizer = models.BooleanField(default=False)
    trust_remote_code_model = models.BooleanField(default=False)
    revision = models.CharField(max_length=255, blank=True, null=True, default="main")


class PromptStructure(models.Model):
    """
    Defines the structure of the prompt for a model.
    system_prefix : str
        The prefix to indicate instructions for the LLM.
    system_tag : str
        The tag to indicate the start of the system prefix for the LLM.
    system_end : str
        The tag to indicate the end of the system prefix for the LLM.
    user_tag : str
        The tag to indicate the start of the user input.
    user_end : str
        The tag to indicate the end of the user input.
    assistant_tag : str
        The tag to indicate the start of the assistant output.
    assistant_end : str
        The tag to indicate the end of the assistant output.
        The tag to indicate the end of the role (system role, user role, assistant role).
    n_contexts_to_use : int, optional
        The number of contexts to use, by default 3
    lang : str, optional
        The language of the prompt, by default 'en'
    model : Model
        The model this prompt structure belongs to.
    """

    system_prefix = models.TextField(blank=True, default="")
    system_tag = models.CharField(max_length=255, blank=True, default="")
    system_end = models.CharField(max_length=255, blank=True, default="")
    user_tag = models.CharField(max_length=255, blank=True, default="<|prompt|>")
    user_end = models.CharField(max_length=255, blank=True, default="\n")
    assistant_tag = models.CharField(max_length=255, blank=True, default="<|answer|>")
    assistant_end = models.CharField(max_length=255, blank=True, default="\n")
    n_contexts_to_use = models.IntegerField(default=3)
    model = models.ForeignKey(Model, on_delete=models.PROTECT)


class GenerationConfig(models.Model):
    """
    Defines the generation configuration for a model.
    top_k : int, optional
        The number of tokens to consider for the top-k sampling, by default 50
    top_p : float, optional
        The cumulative probability for the top-p sampling, by default 1.0
    temperature : float, optional
        The temperature for the sampling, by default 1.0
    repetition_penalty : float, optional
        The repetition penalty for the sampling, by default 1.0
    seed : int, optional
        The seed for the sampling, by default 42
    max_new_tokens : int, optional
        The maximum number of new tokens to generate, by default 256
    model : Model
        The model this generation configuration belongs to.
    """
    top_k = models.IntegerField(default=50)
    top_p = models.FloatField(default=1.0)
    temperature = models.FloatField(default=1.0)
    repetition_penalty = models.FloatField(default=1.0)
    seed = models.IntegerField(default=42)
    max_new_tokens = models.IntegerField(default=256)
    model = models.ForeignKey(Model, on_delete=models.PROTECT)
    
