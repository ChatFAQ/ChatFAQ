import csv
from io import StringIO
from django.contrib.postgres.fields import ArrayField
from django.db import models
from back.apps.language_model.tasks import llm_query_task
from back.common.models import ChangesMixin
from fernet_fields import EncryptedCharField
from simple_history.models import HistoricalRecords
from .tasks import parse_pdf_task, parse_url_task


class KnowledgeBase(models.Model):
    """
    A knowledge base groups all its knowledge items under one language and keeps the original file for reference.

    name: str
        Just a name for the knowledge base.
    original_file: File
        The original file used to create the knowledge base.
        Just a name for the dataset.
    original_csv: FileField
        The original CSV file.
    original_pdf: FileField
        The original PDF file.
    original_url: URLField
        The original URL.
    lang: en, es, fr
        The language of the knowledge base.
    """

    LANGUAGE_CHOICES = (
        ("en", "English"),
        ("es", "Spanish"),
        ("fr", "French"),
    )
    name = models.CharField(max_length=255, unique=True)
    original_file = models.FileField(blank=True, null=True)

    STRATEGY_CHOICES = (
        ("auto", "Auto"),
        ("fast", "Fast"),
        ("ocr_only", "OCR Only"),
        ("hi_res", "Hi Res"),
    )

    SPLITTERS_CHOICES = (
        ("sentences", "Sentences"),
        ("words", "Words"),
        ("tokens", "Tokens"),
        ("smart", "Smart"),
    )

    name = models.CharField(max_length=100)
    lang = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default="en")

    # PDF parsing options
    strategy = models.CharField(max_length=10, default="fast", choices=STRATEGY_CHOICES)
    splitter = models.CharField(max_length=10, default="sentences", choices=SPLITTERS_CHOICES)
    chunk_size = models.IntegerField(default=128)
    chunk_overlap = models.IntegerField(default=16)
    recursive = models.BooleanField(default=True)

    original_csv = models.FileField(blank=True, null=True)
    original_pdf = models.FileField(blank=True, null=True)
    original_url = models.URLField(blank=True, null=True)


    def update_items_from_csv(self):
        csv_content = self.original_csv.read().decode("utf-8").splitlines()
        csv_rows = csv.DictReader(csv_content)

        new_items = [
            KnowledgeItem(
                dataset=self,
                intent=row["intent"],
                answer=row["answer"],
                url=row["url"],
                section=row.get("section"),
                role=row.get("role"),
            )
            for row in csv_rows
        ]

        KnowledgeItem.objects.filter(dataset=self).delete() # TODO: give the option to reset the dataset or not, if reset is True, pass the last date of the last item to the spider and delete them when the crawling finisges
        KnowledgeItem.objects.bulk_create(new_items)

    def to_csv(self):
        items = KnowledgeItem.objects.filter(knowledge_base=self)
        f = StringIO()
        writer = csv.DictWriter(f, fieldnames=["title", "content", "url", "section", "role"],)
        writer.writeheader()
        for item in items:
            writer.writerow(
                {
                    "title": item.title,
                    "content": item.content,
                    "url": item.url,
                    "section": item.section,
                    "role": item.role,
                }
            )
        return f.getvalue()

    def __str__(self):
        return self.name or "Dataset {}".format(self.id)

    def save(self, *args, **kw):
        super().save(*args, **kw)
        if self._should_update_items_from_file():
            self.update_items_from_file()

    def _should_update_items_from_file(self):
        if not self.pk:
            return True

        orig = KnowledgeBase.objects.get(pk=self.pk)
        return orig.original_csv != self.original_csv or orig.original_pdf != self.original_pdf

    def update_items_from_file(self):
        if self.original_csv:
            self.update_items_from_csv()
        elif self.original_pdf:
            parse_pdf_task.delay(self.pk)
        elif self.original_url:
            parse_url_task.delay(self.pk, self.original_url)
        llm_query_task.delay(recache_models=True)


class KnowledgeItem(ChangesMixin):
    """
    An item is a question/answer pair.

    knowledge_base: KnowledgeBase
        The knowledge base it belongs to.
    title: str
        The question of the FAQ.
    content: str
        The answer to the FAQ.
    url: str
        The context of the FAQ, usually is the breadcrumb of the page where the FAQ is.
    section: str
        Sometimes the web pages have different user roles and it serves different FAQs to each one of them.
    role: str
        The URL of the page where the FAQ is.
    embedding: VectorField
        A computed embedding for the model.
    """

    knowledge_base = models.ForeignKey(KnowledgeBase, on_delete=models.CASCADE)
    title = models.TextField(blank=True, null=True)
    content = models.TextField()
    url = models.URLField(max_length=2083)
    section = models.TextField(blank=True, null=True)
    role = models.CharField(max_length=255, blank=True, null=True)
    embedding = ArrayField(models.FloatField(), blank=True, null=True)
    page_number = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.content} ds ({self.knowledge_base.pk})"


class AutoGeneratedTitle(models.Model):
    """
    An utterance is a synonym of an item.

    knowledge_item: KnowledgeItem
        The knowledge item this synonym refers to.
    title: str
        The synonym of the item.
    embedding: VectorField
        A computed embedding for the model.
    """

    knowledge_item = models.ForeignKey(KnowledgeItem, on_delete=models.CASCADE)
    title = models.TextField()
    embedding = ArrayField(models.FloatField(), blank=True, null=True)


class RAGConfig(models.Model):
    """
    It relates the different elements to create a RAG (Retrieval Augmented Generation) pipeline
    """
    name = models.CharField(max_length=255, unique=True)
    knowledge_base = models.ForeignKey(KnowledgeBase, on_delete=models.CASCADE)
    llm_config = models.ForeignKey("LLMConfig", on_delete=models.PROTECT)
    prompt_config = models.ForeignKey("PromptConfig", on_delete=models.PROTECT)
    generation_config = models.ForeignKey("GenerationConfig", on_delete=models.PROTECT)


class LLMConfig(models.Model):
    """
    A model config with all the settings to configure an LLM.
    name: str
        Just a name for the model.
    repo_id: str
        The hugginface repo id of the base model.
    status: created, training, trained
        The status of the model.
    ggml_model_filename: str
        The GGML filename of the model.
    model_config: str
        The huggingface model config of the model.
    auth_token: str
        An auth token to access models, it could be a huggingface token, openai token, etc.
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

    name = models.CharField(max_length=255, unique=True)
    repo_id = models.CharField(max_length=100, default="google/flan-t5-base")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="created")
    ggml_model_filename = models.CharField(max_length=255, blank=True, null=True)
    model_config = models.CharField(max_length=255, blank=True, null=True)
    auth_token = EncryptedCharField(max_length=255, blank=True, null=True)
    load_in_8bit = models.BooleanField(default=False)
    use_fast_tokenizer = models.BooleanField(default=True)
    trust_remote_code_tokenizer = models.BooleanField(default=False)
    trust_remote_code_model = models.BooleanField(default=False)
    revision = models.CharField(max_length=255, blank=True, null=True, default="main")

    def __str__(self):
        return self.name


class PromptConfig(models.Model):
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
    name = models.CharField(max_length=255, unique=True)
    system_prefix = models.TextField(blank=True, default="")
    system_tag = models.CharField(max_length=255, blank=True, default="")
    system_end = models.CharField(max_length=255, blank=True, default="")
    user_tag = models.CharField(max_length=255, blank=True, default="<|prompt|>")
    user_end = models.CharField(max_length=255, blank=True, default="")
    assistant_tag = models.CharField(max_length=255, blank=True, default="<|answer|>")
    assistant_end = models.CharField(max_length=255, blank=True, default="")
    n_contexts_to_use = models.IntegerField(default=3)
    history = HistoricalRecords()

    def __str__(self):
        return self.name


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
    name = models.CharField(max_length=255, unique=True)
    top_k = models.IntegerField(default=50)
    top_p = models.FloatField(default=1.0)
    temperature = models.FloatField(default=1.0)
    repetition_penalty = models.FloatField(default=1.0)
    seed = models.IntegerField(default=42)
    max_new_tokens = models.IntegerField(default=256)

    def __str__(self):
        return self.name

