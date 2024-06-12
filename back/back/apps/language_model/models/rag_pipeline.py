import os
import uuid
from urllib.parse import urljoin

from django.db import models, transaction
from django.conf import settings
from pgvector.django import MaxInnerProduct

from simple_history.models import HistoricalRecords

from back.apps.language_model.models.enums import IndexStatusChoices, DeviceChoices, RetrieverTypeChoices, LLMChoices
from back.apps.language_model.models.data import KnowledgeBase, KnowledgeItem
from back.common.models import ChangesMixin

from back.apps.language_model.tasks import index_task
from back.apps.language_model.ray_deployments import launch_rag_deployment

from logging import getLogger

logger = getLogger(__name__)


# First, define the Manager subclass.
class EnabledRAGConfigManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(enabled=True)


class RAGConfig(ChangesMixin):
    """
    It relates the different elements to create a RAG (Retrieval Augmented Generation) pipeline
    """

    objects = models.Manager()  # The default manager.
    enabled_objects = EnabledRAGConfigManager()  # The Dahl-specific manager.

    name = models.CharField(max_length=255, unique=True)
    knowledge_base = models.ForeignKey(KnowledgeBase, on_delete=models.CASCADE)
    llm_config = models.ForeignKey("LLMConfig", on_delete=models.PROTECT)
    prompt_config = models.ForeignKey("PromptConfig", on_delete=models.PROTECT)
    generation_config = models.ForeignKey("GenerationConfig", on_delete=models.PROTECT)
    retriever_config = models.ForeignKey("RetrieverConfig", on_delete=models.PROTECT)
    enabled = models.BooleanField(default=True)
    s3_index_path = models.CharField(max_length=255, blank=True, null=True, editable=False)
    num_replicas = models.IntegerField(default=1)

    index_status = models.CharField(
        max_length=20,
        choices=IndexStatusChoices.choices,
        default=IndexStatusChoices.NO_INDEX,
        editable=False
    )

    def generate_s3_index_path(self):
        unique_id = str(uuid.uuid4())[:8]
        return f'indexes/{self.name}_index_{unique_id}'

    def get_index_status(self):
        return IndexStatusChoices(self.index_status)

    def get_deploy_name(self):
        return f'rag_{self.name}'

    def __str__(self):
        return self.name if self.name is not None else f"{self.llm_config.name} - {self.knowledge_base.name}"

    # When saving we want to check if the llm_config has changed and in that reload the RAG
    def save(self, *args, **kwargs):
        redeploy_rag = False

        if self.pk is not None:
            old = RAGConfig.objects.get(pk=self.pk)
            if self.name != old.name:
                redeploy_rag = True
                logger.info(f"RAG config name changed...")
            if self.llm_config != old.llm_config:
                redeploy_rag = True
                logger.info(f"RAG config {self.name} changed llm config...")
            if not old.enabled and self.enabled: # If the config was disabled and now is enabled
                redeploy_rag = True
                logger.info(f"RAG config {self.name} {'enabled' if self.enabled else 'disabled'} changed llm config...")
            if self.knowledge_base != old.knowledge_base:
                self.index_status = IndexStatusChoices.NO_INDEX
                logger.info(f"RAG config {self.name} changed knowledge base. Index needs to be updated...")
            if self.retriever_config.model_name != old.retriever_config.model_name or self.retriever_config.get_retriever_type() != old.retriever_config.get_retriever_type():
                self.index_status = IndexStatusChoices.NO_INDEX
                logger.info(f"RAG config {self.name} changed retriever model. Index needs to be updated...")

        super().save(*args, **kwargs)

        if redeploy_rag and self.enabled:
            def on_commit_callback():
                task_name = f"launch_rag_deployment_{self.name}"
                print(f"Submitting the {task_name} task to the Ray cluster...")
                launch_rag_deployment.options(name=task_name).remote(self.id)

            # Schedule the task to run after the transaction is committed
            transaction.on_commit(on_commit_callback)

    def trigger_reindex(self):
        logger.info(f"Launching RAG reindex for {self.name}")
        index_task.remote(self.id, launch_rag_deploy=self.enabled)

    def trigger_deploy(self):
        """Deploys should be automatically triggered when the RAG is saved, but this method is here for manual triggering if needed."""
        if self.enabled and self.get_index_status() in [IndexStatusChoices.OUTDATED, IndexStatusChoices.UP_TO_DATE]:
            logger.info(f"Launching RAG deploy for {self.name}")
            task_name = f"launch_rag_deployment_{self.name}"
            logger.info(f"Submitting the {task_name} task to the Ray cluster...")
            launch_rag_deployment.options(name=task_name).remote(self.id)
        else:
            logger.info(f"RAG {self.name} is not enabled or index is not up to date, skipping deploy")

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
        rag_config : RAGConfig
            RAGConfig to be used for filtering the KnowledgeItems.
        """
        items_for_query = (
                KnowledgeItem.objects.filter(embedding__rag_config=self)
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


class RetrieverConfig(ChangesMixin):
    """
    A config with all the settings to configure the retriever.
    name: str
        Just a name for the retriever.
    model_name: str
        The name of the retriever model to use. It must be a HuggingFace repo id.
    retriever_type: str
        The type of retriever to use.
    batch_size: int
        The batch size to use for the retriever.
    device: str
        The device to use for the retriever.
    """

    name = models.CharField(max_length=255, unique=True)
    model_name = models.CharField(max_length=255, default="colbert-ir/colbertv2.0") # For dev and demo purposes.
    retriever_type = models.CharField(max_length=10, choices=RetrieverTypeChoices.choices, default=RetrieverTypeChoices.COLBERT)
    batch_size = models.IntegerField(default=1) # batch size 1 for better default cpu generation
    device = models.CharField(max_length=10, choices=DeviceChoices.choices, default=DeviceChoices.CPU)

    def __str__(self):
        return self.name

    def get_retriever_type(self):
        return RetrieverTypeChoices(self.retriever_type)

    def get_device(self):
        return DeviceChoices(self.device)

    # When saving we want to check if the model_name has changed and in that case regenerate all the embeddings for the
    # knowledge bases that uses this retriever.
    def save(self, *args, **kwargs):
        logger.info('Checking if we need to generate embeddings because of a retriever config change')
        rags_to_redeploy = None
        if self.pk is not None:
            old_retriever = RetrieverConfig.objects.get(pk=self.pk)

            if self.model_name != old_retriever.model_name or self.get_retriever_type() != old_retriever.get_retriever_type():
                # If the model or model type has changed we need to reindex and not redeploy the RAGs until the index is ready
                rag_configs = RAGConfig.objects.filter(retriever_config=self)
                for rag_config in rag_configs:
                    rag_config.index_status = IndexStatusChoices.NO_INDEX
                    rag_config.save()

            if self.get_device() != old_retriever.get_device():
                # if the device has changed we need to redeploy all the RAGs that use this retriever
                rags_to_redeploy = RAGConfig.objects.filter(retriever_config=self)


        super().save(*args, **kwargs)

        if rags_to_redeploy:
            def on_commit_callback():
                logger.info('Retriever device changed, launching rag redeploys')
                for rag in rags_to_redeploy:
                    if rag.enabled:
                        task_name = f"launch_rag_deployment_{rag.name}"
                        logger.info(f"Submitting the {task_name} task to the Ray cluster...")
                        launch_rag_deployment.options(name=task_name).remote(rag.id)

            # Schedule the task to run after the transaction is committed
            transaction.on_commit(on_commit_callback)


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
    """

    name = models.CharField(max_length=255, unique=True)
    llm_type = models.CharField(max_length=10, choices=LLMChoices.choices, default=LLMChoices.OPENAI)
    llm_name = models.CharField(max_length=100, default="gpt-4o")
    base_url = models.CharField(max_length=255, blank=True, null=True)
    model_max_length = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name

    def get_llm_type(self):
        return LLMChoices(self.llm_type)

    def save(self, *args, **kwargs):
        logger.info('Checking if we need to redeploy RAGs because of a LLM config change')
        rags_to_redeploy = None
        if self.pk is not None:
            old_llm = LLMConfig.objects.get(pk=self.pk)

            if self.llm_name != old_llm.llm_name or self.get_llm_type() != old_llm.get_llm_type():
                # change the rag config index status to NO_INDEX
                rags_to_redeploy = RAGConfig.objects.filter(llm_config=self)

        super().save(*args, **kwargs)

        if rags_to_redeploy:
            def on_commit_callback():
                logger.info('LLM changed, launching rag redeploys')
                for rag in rags_to_redeploy:
                    if rag.enabled:
                        task_name = f"launch_rag_deployment_{rag.name}"
                        logger.info(f"Submitting the {task_name} task to the Ray cluster...")
                        launch_rag_deployment.options(name=task_name).remote(rag.id)

            # Schedule the task to run after the transaction is committed
            transaction.on_commit(on_commit_callback)


class PromptConfig(ChangesMixin):
    """
    Defines the structure of the prompt for a model.
    system_prompt : str
        The prompt to indicate instructions for the LLM.
    n_contexts_to_use : int, optional
        The number of contexts to use, by default 3
    """
    name = models.CharField(max_length=255, unique=True)
    system_prompt = models.TextField(blank=True, default="")
    n_contexts_to_use = models.IntegerField(default=5)
    history = HistoricalRecords()

    def __str__(self):
        return self.name


class GenerationConfig(ChangesMixin):
    """
    Defines the generation configuration for a model.
    temperature : float, optional
        The temperature for the sampling, by default 0.2
    max_new_tokens : int, optional
        The maximum number of new tokens to generate, by default 256
    seed : int, optional
        The seed for the sampling, by default 42
    """
    name = models.CharField(max_length=255, unique=True)
    temperature = models.FloatField(default=0.2)
    max_tokens = models.IntegerField(default=1024)
    seed = models.IntegerField(default=42)    

    def __str__(self):
        return self.name
