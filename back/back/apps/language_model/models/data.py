import csv
from io import StringIO
from logging import getLogger

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.apps import apps
from back.apps.language_model.tasks import parse_pdf_task, parse_url_task, llm_query_task, generate_embeddings_task
from back.common.models import ChangesMixin

logger = getLogger(__name__)


class KnowledgeBase(ChangesMixin):
    """
    A knowledge base groups all its knowledge items under one language and keeps the original file for reference.

    name: str
        Just a name for the knowledge base.
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
                knowledge_base=self,
                title=row["title"],
                content=row["content"],
                url=row["url"],
                section=row.get("section"),
                role=row.get("role"),
            )
            for row in csv_rows
        ]

        KnowledgeItem.objects.filter(knowledge_base=self).delete()  # TODO: give the option to reset the dataset or not, if reset is True, pass the last date of the last item to the spider and delete them when the crawling finisges
        KnowledgeItem.objects.bulk_create(new_items)
        self.trigger_generate_embeddings()

    def trigger_generate_embeddings(self):
        RAGConfig = apps.get_model("language_model", "RAGConfig")
        Embedding = apps.get_model("language_model", "Embedding")

        rag_configs = RAGConfig.objects.filter(knowledge_base=self)
        last_i = rag_configs.count() - 1
        for i, rag_config in enumerate(rag_configs.all()):
            # remove all existing embeddings for this rag config
            Embedding.objects.filter(rag_config=rag_config).delete()
            generate_embeddings_task.delay(
                list(self.knowledgeitem_set.values_list("pk", flat=True)),
                rag_config.pk,
                recache_models=(i == last_i)
            )

    def to_csv(self):
        items = KnowledgeItem.objects.filter(knowledge_base=self)
        f = StringIO()

        fieldnames = ["title", "content", "url", "section", "role", "page_number"]

        writer = csv.DictWriter(f, fieldnames=fieldnames,)
        writer.writeheader()

        for item in items:
            row = {
                    "title": item.title if item.title else None,
                    "content": item.content,
                    "url": item.url if item.url else None,
                    "section": item.section if item.section else None,
                    "role": item.role if item.role else None,
                    "page_number": item.page_number if item.page_number else None,
                }
            writer.writerow(row)

        return f.getvalue()

    def get_data(self):
        items = KnowledgeItem.objects.filter(knowledge_base=self)
        logger.info(f'Retrieving items from knowledge base "{self.name}')
        logger.info(f"Number of retrieved items: {len(items)}")
        result = {}
        for item in items:
            result.setdefault("title", []).append(item.title)
            result.setdefault("content", []).append(item.content)
            result.setdefault("url", []).append(item.url)
            result.setdefault("section", []).append(item.section)
            result.setdefault("role", []).append(item.role)
            result.setdefault("page_number", []).append(item.page_number)

        return result

    def __str__(self):
        return self.name or "Knowledge Base {}".format(self.id)

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
            logger.info("Updating items from CSV")
            self.update_items_from_csv()
        elif self.original_pdf:
            logger.info("Updating items from PDF")
            parse_pdf_task.delay(self.pk)
        elif self.original_url:
            logger.info("Updating items from URL")
            parse_url_task.delay(self.pk, self.original_url)
        llm_query_task.delay(recache_models=True, log_caller="KnowledgeBase.update_items_from_file")


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
    page_number = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.content} ds ({self.knowledge_base.pk})"

    # When saving we want to check if the content has changed and in that case regenerate
    # all the embeddings for the rag_config this item belongs to.
    def save(self, *args, **kwargs):
        changes = False
        if self.pk is not None:
            old_item = KnowledgeItem.objects.get(pk=self.pk)
            if self.content != old_item.content:
                changes = True
        super().save(*args, **kwargs)
        if changes:
            self.trigger_generate_embeddings()

    def trigger_generate_embeddings(self):
        RAGConfig = apps.get_model("language_model", "RAGConfig")
        Embedding = apps.get_model("language_model", "Embedding")
        rag_configs = RAGConfig.objects.filter(knowledge_base=self.knowledge_base)
        last_i = rag_configs.count() - 1

        for i, rag_config in enumerate(rag_configs.all()):
            # remove the embedding for this item for this rag config
            Embedding.objects.filter(rag_config=rag_config, knowledge_item=self).delete()
            generate_embeddings_task.delay(
                [self.pk],
                rag_config.pk,
                recache_models=(i == last_i) # recache models if we are in the last iteration
            )


class Embedding(ChangesMixin):
    """
    Embedding representation for a KnowledgeItem.

    knowledge_item: KnowledgeItem
        The KnowledgeItem associated with this embedding.
    embedding: ArrayField
        The actual embedding values.
    """

    knowledge_item = models.ForeignKey(KnowledgeItem, on_delete=models.CASCADE)
    rag_config = models.ForeignKey("RAGConfig", on_delete=models.CASCADE)
    embedding = ArrayField(models.FloatField(), blank=True, null=True)

    def __str__(self):
        return f"Embedding for {self.knowledge_item}"
