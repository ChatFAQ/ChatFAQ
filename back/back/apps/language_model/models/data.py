import csv
from io import StringIO

from django.contrib.postgres.fields import ArrayField
from django.db import models

from back.apps.language_model.tasks import parse_pdf_task, parse_url_task, llm_query_task
from back.common.models import ChangesMixin


class KnowledgeBase(models.Model):
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
