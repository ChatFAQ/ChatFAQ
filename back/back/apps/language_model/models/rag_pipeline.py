import os
import uuid

from django.db import models, transaction
from django.core.files.storage import default_storage
from simple_history.models import HistoricalRecords

from back.apps.language_model.models.data import KnowledgeBase
from back.common.models import ChangesMixin

from back.utils.celery import recache_models
from back.apps.language_model.tasks import delete_index_files_task, index_task

from logging import getLogger

logger = getLogger(__name__)

LLM_CHOICES = (
    ('local_cpu', 'Local CPU Model'),  # GGML models optimized for CPU inference
    ('local_gpu', 'Local GPU Model'),  # Use locally VLLM or HuggingFace for GPU inference.
    ('vllm', 'VLLM Client'),  # Access VLLM engine remotely
    ('openai', 'OpenAI Model'),  # ChatGPT models from OpenAI
    ('claude', 'Claude Model'),  # Claude models from Anthropic
    ('mistral', 'Mistral Model'),  # Mistral models from Mistral
)


# First, define the Manager subclass.
class EnabledRAGConfigManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(disabled=False)


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
    disabled = models.BooleanField(default=False)
    index_up_to_date = models.BooleanField(default=False, editable=False)
    s3_index_path = models.CharField(max_length=255, blank=True, null=True, editable=False)

    def generate_s3_index_path(self):
        unique_id = str(uuid.uuid4())[:8]
        self.s3_index_path = f'indexes/{self.name}_index_{unique_id}'
        self.save()

    def __str__(self):
        return self.name if self.name is not None else f"{self.llm_config.name} - {self.knowledge_base.name}"

    # When saving we want to check if the llm_config has changed and in that reload the RAG
    def save(self, *args, **kwargs):
        load_new_llm = False

        if self.pk is not None:
            old = RAGConfig.objects.get(pk=self.pk)
            if self.llm_config != old.llm_config:
                load_new_llm = True
                logger.info(f"RAG config {self.name} changed llm config...")
            if self.disabled != old.disabled:
                load_new_llm = True
                logger.info(f"RAG config {self.name} {'disabled' if self.disabled else 'enabled'} changed llm config...")
            if self.knowledge_base != old.knowledge_base:
                self.index_up_to_date = False
                logger.info(f"RAG config {self.name} changed knowledge base. Index needs to be updated...")
            if self.retriever_config.model_name != old.retriever_config.model_name:
                self.index_up_to_date = False
                logger.info(f"RAG config {self.name} changed retriever model. Index needs to be updated...")

        super().save(*args, **kwargs)

        if load_new_llm:
            def on_commit_callback():
                recache_models("RAGConfig.save")

            # Schedule the recache_models function to be called
            transaction.on_commit(on_commit_callback)

    def trigger_reindex(self, recache_models: bool = False, logger_name: str = None):
        index_task.delay(self.id, recache_models=recache_models, logger_name=logger_name)  # Trigger the Celery task


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
    DEVICE_CHOICES = (
        ('cpu', 'CPU'),
        ('cuda', 'GPU'),
    )

    RETRIEVER_TYPE_CHOICES = (
        ('colbert', 'ColBERT Search'),
        ('e5', 'Standard Semantic Search'),
    )

    name = models.CharField(max_length=255, unique=True)
    model_name = models.CharField(max_length=255, default="colbert-ir/colbertv2.0") # For dev and demo purposes.
    retriever_type = models.CharField(max_length=10, choices=RETRIEVER_TYPE_CHOICES, default="colbert")
    batch_size = models.IntegerField(default=1) # batch size 1 for better default cpu generation
    device = models.CharField(max_length=10, choices=DEVICE_CHOICES, default="cpu")

    def __str__(self):
        return self.name

    # When saving we want to check if the model_name has changed and in that case regenerate all the embeddings for the
    # knowledge bases that uses this retriever.
    def save(self, *args, **kwargs):
        logger.info('Checking if we need to generate embeddings because of a retriever config change')
        device_changed = False

        if self.pk is not None:
            old_retriever = RetrieverConfig.objects.get(pk=self.pk)

            if self.model_name != old_retriever.model_name or self.retriever_type != old_retriever.retriever_type:
                # change the rag config index_up_to_date to False
                rag_configs = RAGConfig.objects.filter(retriever_config=self)
                for rag_config in rag_configs:
                    rag_config.index_up_to_date = False
                    rag_config.save()

            if self.device != old_retriever.device:
                device_changed = True

        super().save(*args, **kwargs)

        if device_changed:
            def on_commit_callback():
                recache_models("RetrieverConfig.save")

            # Schedule the recache_models function to be called
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
    ggml_model_filename: str
        The GGML filename of the model, if it is a GGML model.
    model_config: str
        The huggingface model config of the model, needed for GGML models.
    load_in_8bit: bool
        Whether to load the model in 8bit or not.
    use_fast_tokenizer: bool
        Whether to use the fast tokenizer or not.
    trust_remote_code_tokenizer: bool
        Whether to trust the remote code for the tokenizer or not.
    trust_remote_code_model: bool
        Whether to trust the remote code for the model or not.
    revision: str
        The specific model version to use. It can be a branch name, a tag name, or a commit id, since we use a git-based system for storing models
    model_max_length: int
        The maximum length of the model.
    """

    name = models.CharField(max_length=255, unique=True)
    llm_type = models.CharField(max_length=10, choices=LLM_CHOICES, default="local_gpu")
    llm_name = models.CharField(max_length=100, default="gpt2")
    ggml_llm_filename = models.CharField(max_length=255, blank=True, null=True)
    model_config = models.CharField(max_length=255, blank=True, null=True)
    load_in_8bit = models.BooleanField(default=False)
    use_fast_tokenizer = models.BooleanField(default=True)
    trust_remote_code_tokenizer = models.BooleanField(default=False)
    trust_remote_code_model = models.BooleanField(default=False)
    revision = models.CharField(max_length=255, blank=True, null=True, default="main")
    model_max_length = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name


class PromptConfig(ChangesMixin):
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
    n_contexts_to_use : int, optional
        The number of contexts to use, by default 3
    """
    name = models.CharField(max_length=255, unique=True)
    system_prefix = models.TextField(blank=True, default="")
    system_tag = models.CharField(max_length=255, blank=True, default="")
    system_end = models.CharField(max_length=255, blank=True, default="")
    user_tag = models.CharField(max_length=255, blank=True, default="<|prompt|>")
    user_end = models.CharField(max_length=255, blank=True, default="")
    assistant_tag = models.CharField(max_length=255, blank=True, default="<|answer|>")
    assistant_end = models.CharField(max_length=255, blank=True, default="")
    n_contexts_to_use = models.IntegerField(default=5)
    history = HistoricalRecords()

    def __str__(self):
        return self.name


class GenerationConfig(ChangesMixin):
    """
    Defines the generation configuration for a model.
    top_k : int, optional
        The number of tokens to consider for the top-k sampling, by default 50
    top_p : float, optional
        The cumulative probability for the top-p sampling, by default 1.0
    temperature : float, optional
        The temperature for the sampling, by default 0.2
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
    temperature = models.FloatField(default=0.2)
    repetition_penalty = models.FloatField(default=1.0)
    seed = models.IntegerField(default=42)
    max_new_tokens = models.IntegerField(default=512)

    def __str__(self):
        return self.name
