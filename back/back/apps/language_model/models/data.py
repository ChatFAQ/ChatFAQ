import csv
from io import StringIO
from logging import getLogger
from uuid import uuid4
import base64
import os

from django.db import models
from django.apps import apps
from django.core.files.base import ContentFile

from back.apps.language_model.models.enums import LanguageChoices, StrategyChoices, SplittersChoices, IndexStatusChoices
from back.apps.broker.models import RemoteSDKParsers
from back.apps.language_model.models.tasks import RayTaskState
from back.apps.language_model.tasks import (
    parse_pdf_task,
    parse_url_task,
)
from back.common.models import ChangesMixin
from pgvector.django import VectorField

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from back.config.storage_backends import select_private_storage



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

    name = models.CharField(max_length=255, unique=True)

    lang = models.CharField(max_length=2, choices=LanguageChoices.choices, default=LanguageChoices.EN)

    def get_lang(self):
        return LanguageChoices(self.lang)

    def to_csv(self):
        items = KnowledgeItem.objects.filter(knowledge_base=self)
        f = StringIO()

        fieldnames = ["title", "content", "url", "section", "role", "page_number"]

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
        )
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


class DataSource(ChangesMixin):

    knowledge_base = models.ForeignKey(KnowledgeBase, on_delete=models.CASCADE)

    # CSV parsing options
    csv_header = models.BooleanField(default=True)
    title_index_col = models.IntegerField(default=0)
    content_index_col = models.IntegerField(default=1)
    url_index_col = models.IntegerField(default=2)
    section_index_col = models.IntegerField(default=3)
    role_index_col = models.IntegerField(default=4)
    page_number_index_col = models.IntegerField(default=5)
    # PDF parsing options
    strategy = models.CharField(max_length=10, choices=StrategyChoices.choices, default=StrategyChoices.FAST)
    # URL parsing options
    recursive = models.BooleanField(default=True)
    # PDF & URL parsing options
    splitter = models.CharField(
        max_length=10, choices=SplittersChoices.choices, default=SplittersChoices.SENTENCES
    )
    chunk_size = models.IntegerField(default=128)
    chunk_overlap = models.IntegerField(default=16)

    original_csv = models.FileField(blank=True, null=True, storage=select_private_storage)
    original_pdf = models.FileField(blank=True, null=True, storage=select_private_storage)
    original_url = models.URLField(blank=True, null=True)

    parser = models.CharField(max_length=255, null=True, blank=True)

    def get_strategy(self):
        return StrategyChoices(self.strategy)

    def get_splitter(self):
        return SplittersChoices(self.splitter)

    def update_items_with_remote_parser(self):
        KnowledgeItem.objects.filter(
            data_source=self
        ).delete()  # TODO: give the option to reset the dataset or not, if reset is True, pass the last date of the last item to the spider and delete them when the crawling finishes
        channel_layer = get_channel_layer()
        layer_name = RemoteSDKParsers.get_next_consumer_group_name(self.parser)
        if layer_name:
            task = RayTaskState(
                task_id=str(uuid4()),
                name=f"{self.parser}_parser",
                func_or_class_name=self.parser,
            )
            task.save()
            async_to_sync(channel_layer.send)(
                layer_name,
                {
                    "type": "send_data_source_to_parse",
                    "parser": self.parser,
                    "payload": {
                        "kb_id": self.knowledge_base.pk,
                        "ds_id": self.pk,
                        "task_id": task.task_id,
                        "csv": self.original_csv.url if self.original_csv else None,
                        "pdf": self.original_pdf.url if self.original_pdf else None,
                        "url": self.original_url,
                    },
                },
            )
        else:
            logger.error(f"No parser available for {self.parser}")
            raise Exception(f"No parser available for {self.parser}")

    def update_items_from_csv(self):
        csv_content = self.original_csv.read().decode("utf-8")
        csv_rows = csv.reader(StringIO(csv_content))
        if self.csv_header:
            next(csv_rows)
        new_items = [
            KnowledgeItem(
                knowledge_base=self.knowledge_base,
                data_source=self,
                title=row[self.title_index_col]
                if len(row) > self.title_index_col
                else "",
                content=row[self.content_index_col]
                if len(row) > self.content_index_col
                else "",
                url=row[self.url_index_col] if len(row) > self.url_index_col else "",
                section=row[self.section_index_col]
                if len(row) > self.section_index_col
                else "",
                role=row[self.role_index_col] if len(row) > self.role_index_col else "",
            )
            for row in csv_rows
        ]

        KnowledgeItem.objects.filter(
            data_source=self
        ).delete()  # TODO: give the option to reset the dataset or not, if reset is True, pass the last date of the last item to the spider and delete them when the crawling finishes
        KnowledgeItem.objects.bulk_create(new_items)

    def save(self, *args, **kw):
        _should_update = self._should_update_items_from_file()
        super().save(*args, **kw)
        if _should_update:
            self.update_items_from_file()

    def _should_update_items_from_file(self):
        if not self.pk:
            return True

        orig = DataSource.objects.get(pk=self.pk)
        return (
            orig.original_csv != self.original_csv
            or orig.original_pdf != self.original_pdf
            or self.parser != orig.parser
        )

    def update_items_from_file(self):
        if self.parser:
            logger.info("Updating items from remote SDK parser")
            self.update_items_with_remote_parser()
        elif self.original_csv:
            logger.info("Updating items from CSV")
            self.update_items_from_csv()
        elif self.original_pdf:
            logger.info("Updating items from PDF")
            task_name = f"parse_pdf__{self.original_pdf.name}"
            logger.info(f"Submitting the {task_name} task to the Ray cluster...")
            parse_pdf_task.options(name=task_name).remote(self.pk)
        elif self.original_url:
            logger.info("Updating items from URL")
            task_name = f"parse_url__{self.original_url}"
            logger.info(f"Submitting the {task_name} task to the Ray cluster...")
            parse_url_task.options(name=task_name).remote(self.pk, self.original_url)


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
    metadata: JSONField
        Metadata for filtering and searching.
    """

    knowledge_base = models.ForeignKey(KnowledgeBase, on_delete=models.CASCADE)
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE, null=True, blank=True, editable=False)
    title = models.TextField(blank=True, null=True)
    content = models.TextField()
    url = models.URLField(max_length=2083, null=True, blank=True)
    section = models.TextField(blank=True, null=True)
    role = models.CharField(max_length=255, blank=True, null=True)
    page_number = models.IntegerField(blank=True, null=True)
    message = models.ManyToManyField("broker.Message", through="MessageKnowledgeItem", editable=False)
    metadata = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.content} ds ({self.knowledge_base.pk})"

    def save(self, *args, **kwargs):

        # get the retriever configs to which this knowledge base belongs
        retriever_configs = apps.get_model("language_model", "RetrieverConfig").objects.filter(
            knowledge_base=self.knowledge_base
        )

        # set the retriever config index status to outdated
        if self.pk is None: # new item
            for retriever_config in retriever_configs:
                retriever_config.index_status = IndexStatusChoices.OUTDATED
                retriever_config.save()
        else: # modified item
            old_item = KnowledgeItem.objects.get(pk=self.pk)
            if self.content != old_item.content:
                for retriever_config in retriever_configs:
                    retriever_config.index_status = IndexStatusChoices.OUTDATED
                    retriever_config.save()

        super().save(*args, **kwargs)

    def get_image_urls(self):
        return {img.image_file.name: img.image_file.url for img in self.knowledgeitemimage_set.all()}

    def to_retrieve_context(self):
        return {
            "knowledge_item_id": self.id,
            "title": self.title,
            "content": self.content,
            "url": self.url,
            "section": self.section,
            "role": self.role,
            "page_number": str(self.page_number) if self.page_number else None,
            "image_urls": self.get_image_urls(),
        }



def gen_safe_url_uuid():
    """Generate a URL safe UUID."""

    base_id = uuid4()

    # Encode the bytes using URL and Filename safe Base64
    url_safe_base64_id = base64.urlsafe_b64encode(base_id.bytes)

    # Convert to string
    url_safe_base64_id_str = url_safe_base64_id.decode("utf-8")

    return url_safe_base64_id_str


def upload_to_uuid(instance, filename):
    """We don't want to keep the original filename, just the extension
    and then a structure of <app>/<model>/<knowledge_base>/<uuid>.<ext>.
    """

    _, ext = os.path.splitext(filename)
    low_ext = ext.lower()
    normal_ext = {
        ".jpeg": ".jpg",
    }.get(low_ext, low_ext)

    base_id = gen_safe_url_uuid()[
        :4
    ]  # shorten the uuid to 4 characters so the LLM doesn't have to write long paths

    meta = instance._meta  # noqa, It's official Django API
    app = meta.app_label
    model = meta.model_name
    kb_name = instance.knowledge_item.knowledge_base.name

    return os.path.join(
        app,
        model,
        kb_name,
        base_id + normal_ext,
    )


class KnowledgeItemImage(models.Model):
    """
    A model representing an image contained in a KnowledgeItem.
    """

    image_file = models.ImageField(upload_to=upload_to_uuid, storage=select_private_storage)
    image_caption = models.TextField(blank=True, null=True)
    knowledge_item = models.ForeignKey(KnowledgeItem, on_delete=models.CASCADE)

    def __init__(self, *args, **kwargs):
        self._base64_image = kwargs.pop("image_base64", None)
        super(KnowledgeItemImage, self).__init__(*args, **kwargs)

    def __str__(self):
        return f"Image for {self.knowledge_item.pk} with caption {self.image_caption} and path {self.image_file.name}"

    def save(self, *args, **kwargs):
        if self._base64_image:
            # Check if there's a data URI scheme and split it off if present
            if ";" in self._base64_image and "base64," in self._base64_image:
                format, imgstr = self._base64_image.split(";base64,")
                ext = format.split("/")[-1]
            else:
                imgstr = self._base64_image
                ext = "jpg"  # Default extension if not provided in the data URI

            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)

            # Save the image file
            self.image_file.save(name=data.name, content=data, save=False)

        super(KnowledgeItemImage, self).save(*args, **kwargs)


class Embedding(ChangesMixin):
    """
    Embedding representation for a KnowledgeItem.
    knowledge_item: KnowledgeItem
        The KnowledgeItem associated with this embedding.
    retriever_config: RetrieverConfig
        The retriever_configs associated with this embedding.
    embedding: ArrayField
        The actual embedding values.
    """

    knowledge_item = models.ForeignKey(KnowledgeItem, on_delete=models.CASCADE, editable=False)
    retriever_config = models.ForeignKey("RetrieverConfig", on_delete=models.CASCADE, editable=False)
    embedding = VectorField(null=True, blank=True, editable=False)

    def __str__(self):
        return f"Embedding for {self.knowledge_item}"


class AutoGeneratedTitle(ChangesMixin):
    """
    An utterance is a synonym of an item.

    knowledge_item: KnowledgeItem
        The knowledge item this synonym refers to.
    title: str
        The synonym of the item.
    embedding: VectorField
        A computed embedding for the model.
    """

    knowledge_item = models.ForeignKey(KnowledgeItem, on_delete=models.CASCADE, editable=False)
    title = models.TextField()
    embedding = VectorField(null=True, blank=True, editable=False)


class Intent(ChangesMixin):
    """
    An intent is a group of utterances.

    name: str
        The name of the intent.
    auto_generated: bool
        If the intent was auto generated or not.
    valid: bool
        If the intent is validated by the admin or not.
    new_intent: bool
        If the intent is new, or if it exists already in the knowledge base.
    message: Message
        The message associated with this intent.
    """

    intent_name = models.CharField(max_length=255, unique=False)
    auto_generated = models.BooleanField(default=False, editable=False)
    valid = models.BooleanField(default=False)
    suggested_intent = models.BooleanField(default=False, editable=False)
    message = models.ManyToManyField("broker.Message", blank=True, editable=False)
    knowledge_item = models.ManyToManyField(KnowledgeItem, blank=True, editable=False)
    # Maybe add a knowledge_base foreign key here for querying simplicity and performance


class MessageKnowledgeItem(ChangesMixin):
    """
    A message can have multiple knowledge items.

    message: Message
        The message associated with this knowledge item.
    knowledge_item: KnowledgeItem
        The knowledge item associated with this message.
    similarity: float
        The similarity between the message and the knowledge item.
    valid: bool
        If the relation is validated by the admin or not.
    """

    message = models.ForeignKey("broker.Message", on_delete=models.CASCADE, editable=False)
    knowledge_item = models.ForeignKey(KnowledgeItem, on_delete=models.CASCADE, editable=False)
    similarity = models.FloatField(null=True, blank=True, editable=False)
    valid = models.BooleanField(default=False)
