import uuid
from logging import getLogger

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from pgvector.django import MaxInnerProduct
from simple_history.models import HistoricalRecords

from back.apps.language_model.models.data import KnowledgeBase, KnowledgeItem
from back.apps.language_model.models.enums import (
    DeviceChoices,
    IndexStatusChoices,
    LLMChoices,
    RetrieverTypeChoices,
)
from back.apps.language_model.ray_deployments import (
    delete_serve_app,
    launch_colbert_deployment,
    launch_e5_deployment,
)
from back.apps.language_model.tasks import index_task
from back.common.models import ChangesMixin
from back.utils import NissaStringField

logger = getLogger(__name__)


class EnabledRetrieverConfigManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(enabled=True)


class RetrieverConfig(ChangesMixin):
    """
    A config with all the settings to configure the retriever.
    name: str
        Just a name for the retriever.
    model_name: str
        The name of the retriever model to use. It must be a HuggingFace repo id.
    retriever_type: str
        The type of retriever to use.
    knowledge_base: KnowledgeBase
        The knowledge base to use for the retriever.
    index_status: str
        The status of the retriever index.
    s3_index_path: str
        The path to the retriever index in S3.
    batch_size: int
        The batch size to use for the retriever.
    device: str
        The device to use for the retriever.
    enabled: bool
        Whether the retriever is enabled.
    num_replicas: int
        The number of replicas to deploy in the Ray cluster.
    """

    objects = models.Manager()  # The default manager.

    enabled_objects = EnabledRetrieverConfigManager()  # The Dahl-specific manager.
    name = models.CharField(max_length=255, unique=True)

    # Model properties
    model_name = models.CharField(
        max_length=255, default="colbert-ir/colbertv2.0"
    )  # For dev and demo purposes.
    retriever_type = models.CharField(
        max_length=10,
        choices=RetrieverTypeChoices.choices,
        default=RetrieverTypeChoices.COLBERT,
    )

    # Knowledge Base properties
    knowledge_base = models.ForeignKey(KnowledgeBase, on_delete=models.CASCADE)
    index_status = models.CharField(
        max_length=20,
        choices=IndexStatusChoices.choices,
        default=IndexStatusChoices.NO_INDEX,
        editable=False,
    )
    s3_index_path = models.CharField(
        max_length=255, blank=True, null=True, editable=False
    )

    # Model inference properties
    batch_size = models.IntegerField(
        default=1
    )  # batch size 1 for better default cpu generation
    device = models.CharField(
        max_length=10, choices=DeviceChoices.choices, default=DeviceChoices.CPU
    )
    enabled = models.BooleanField(default=False)
    num_replicas = models.IntegerField(default=1)

    history = HistoricalRecords()

    def __str__(self):
        return self.name

    def get_retriever_type(self):
        return RetrieverTypeChoices(self.retriever_type)

    def get_device(self):
        return DeviceChoices(self.device)

    def get_deploy_name(self):
        return f"retriever_{self.name}"

    def generate_s3_index_path(self):
        unique_id = str(uuid.uuid4())[:8]
        return f"indexes/{self.name}_index_{unique_id}"

    def get_index_status(self):
        return IndexStatusChoices(self.index_status)

    def trigger_deploy(self):
        """Deploys should be automatically triggered when the Retriever is saved, but this method is here for manual triggering if needed."""
        if self.enabled and self.index_status in [
                IndexStatusChoices.OUTDATED,
                IndexStatusChoices.UP_TO_DATE,
            ]:
            task_name = f"launch_retriever_deployment_{self.name}"
            logger.info(f"Submitting the {task_name} task to the Ray cluster...")
            if self.get_retriever_type() == RetrieverTypeChoices.E5:
                launch_e5_deployment.options(name=task_name).remote(
                    self.get_deploy_name(),
                    self.model_name,
                    self.get_device() == DeviceChoices.CPU,
                    self.pk,
                    self.knowledge_base.get_lang().value,
                    self.num_replicas,
                )
            elif self.get_retriever_type() == RetrieverTypeChoices.COLBERT:
                launch_colbert_deployment.options(name=task_name).remote(
                    self.get_deploy_name(), self.s3_index_path, self.num_replicas
                )
        else:
            logger.info(f"Retriever {self.name} is not enabled, skipping deploy")

    def trigger_reindex(self):
        logger.info(f"Launching Retriever reindex for {self.name}")
        index_task.remote(self.id, launch_retriever_deploy=self.enabled)

    def save(self, *args, **kwargs):
        redeploy_retriever = False
        shutdown_retriever = False

        if self.pk is not None:
            old_retriever = RetrieverConfig.objects.get(pk=self.pk)

            if (
                self.model_name != old_retriever.model_name
                or self.get_retriever_type() != old_retriever.get_retriever_type()
            ):
                redeploy_retriever = True
                self.index_status = IndexStatusChoices.NO_INDEX

            if (
                self.batch_size != old_retriever.batch_size
                or self.get_device() != old_retriever.get_device()
            ):
                redeploy_retriever = True

            if old_retriever.enabled and not self.enabled:
                shutdown_retriever = True
                logger.info(
                    f"Retriever config {self.name} changed to disabled. Shutting down the Retriever deployment..."
                )

            if not old_retriever.enabled and self.enabled:
                redeploy_retriever = True
                logger.info(
                    f"Retriever config {self.name} changed to enabled. Launching the Retriever deployment..."
                )

        super().save(*args, **kwargs)

        if redeploy_retriever and self.enabled:

            def on_commit_callback():
                self.trigger_deploy()

            # Schedule the task to run after the transaction is committed
            transaction.on_commit(on_commit_callback)

        if shutdown_retriever and not self.enabled:

            def on_commit_callback():
                deployment_name = self.get_deploy_name()
                task_name = f"delete_serve_app_{deployment_name}"
                logger.info(f"Submitting the {task_name} task to the Ray cluster...")
                delete_serve_app.options(name=task_name).remote(deployment_name)

            transaction.on_commit(on_commit_callback)

    def retrieve_kitems(self, query_embedding, threshold, top_k):
        """
        Returns the context for the given query_embedding.
        Parameters
        ----------
        query_embedding : torch.Tensor, np.ndarray or list
            Query embedding to be used for retrieval.
        threshold : float
            Threshold for filtering the context.
        top_k : int
            Number of context to be returned. If -1, all context are returned.
        """
        items_for_query = (
            KnowledgeItem.objects.filter(embedding__retriever_config=self)
            .annotate(
                similarity=-MaxInnerProduct("embedding__embedding", query_embedding)
            )
            .filter(similarity__gt=threshold)
            .order_by("-similarity")
        )

        if top_k != -1:
            items_for_query = items_for_query[:top_k]

        query_results = [
            {
                "k_item_id": item.id,
                "content": item.content,
                "similarity": item.similarity,
            }
            for item in items_for_query
        ]
        return query_results


class EnabledLLMConfigManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(enabled=True)


class LLMConfig(ChangesMixin):
    """
     A model config with all the settings to configure an LLM.
     name: str
         Just a name for the model.
     llm_type: str
         The type of LLM to use.
     llm_name: str
         The name of the LLM to use. It can be a HuggingFace repo id, an OpenAI model id, etc.
     base_url: str
         The base url where the model is hosted. It is used for vLLM deployments and Together LLM Endpoints.
     model_max_length: int
         The maximum length of the model.
     api_key: str (encrypted)
         Optional API key for the LLM. Will be stored encrypted in the database.
     enabled: bool
         Whether the LLM is enabled.
     num_replicas: int
         The number of replicas to deploy in the Ray cluster.
    """

    objects = models.Manager()
    enabled_objects = EnabledLLMConfigManager()

    name = models.CharField(max_length=255, unique=True)
    llm_type = models.CharField(
        max_length=10, choices=LLMChoices.choices, default=LLMChoices.OPENAI
    )
    llm_name = models.CharField(max_length=100, default="gpt-4o")
    base_url = models.CharField(max_length=255, blank=True, null=True)
    model_max_length = models.IntegerField(blank=True, null=True)
    api_key = NissaStringField(
        blank=True,
        null=True,
        help_text="Optional API key for the LLM. This value will be stored encrypted. Note: API keys can only be saved when encryption is properly configured."
    )
    enabled = models.BooleanField(default=False)
    num_replicas = models.IntegerField(default=1)

    history = HistoricalRecords()

    def clean(self):
        super().clean()
        if self.api_key and not settings.AZOR_PRIVATE_KEY:
            raise ValidationError({
                'api_key': 'Cannot save API key when encryption is not configured. Please configure AZOR_PRIVATE_KEY first.'
            })

    def save(self, *args, **kwargs):
        self.clean()  # Run validation before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_llm_type(self):
        return LLMChoices(self.llm_type)


# ============================================================
# NOTE: Prompt and Generation Config Usage
# ------------------------------------------------------------
# Currently, these configurations are not used anywhere.
# In the future they may be used from the SDK
# ============================================================
class PromptConfig(ChangesMixin):
    """
    Defines the structure of the prompt for a model.
    prompt : str
        The prompt to indicate instructions for the LLM.
    """

    name = models.CharField(max_length=255, unique=True)
    prompt = models.TextField(blank=False, default="")

    history = HistoricalRecords()

    def __str__(self):
        return self.name


class GenerationConfig(ChangesMixin):
    """
    Defines the generation configuration for a model.
    temperature : float, optional
        The temperature for the sampling, by default 0.2
    max_tokens : int, optional
        The maximum number of new tokens to generate, by default 256
    seed : int, optional
        The seed for the sampling, by default 42
    """

    name = models.CharField(max_length=255, unique=True)
    temperature = models.FloatField(default=0.2)
    max_tokens = models.IntegerField(default=1024)
    seed = models.IntegerField(default=42)

    history = HistoricalRecords()

    def __str__(self):
        return self.name
