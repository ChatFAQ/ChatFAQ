import gc
import uuid
from io import BytesIO
from logging import getLogger
from asgiref.sync import async_to_sync
from celery import Task
from channels.layers import get_channel_layer
from chat_rag import RAG
from chat_rag.llms import (
    GGMLModel,
    HFModel,
    OpenAIChatModel,
    VLLMModel,
    ClaudeChatModel,
    MistralChatModel,
)
from chat_rag.exceptions import PromptTooLongException, RequestException, ModelNotFoundException
from scrapy.utils.project import get_project_settings
from django.db import transaction
from django.apps import apps
from back.config.celery import app
from back.utils import is_celery_worker
from django.forms.models import model_to_dict
from scrapy.crawler import CrawlerRunner
from crochet import setup
from django.conf import settings
import os

from back.utils.celery import recache_models as recache_models_utils
from django.db.models import F


if is_celery_worker():
    setup()

logger = getLogger(__name__)

LLM_CLASSES = {
    "local_cpu": GGMLModel,
    "local_gpu": HFModel,
    "vllm": VLLMModel,
    "openai": OpenAIChatModel,
    "claude": ClaudeChatModel,
    "mistral": MistralChatModel,
}


def get_model(
    llm_name: str,
    llm_type: str,
    ggml_model_filename: str = None,
    use_cpu: bool = False,
    model_config: str = None,
    load_in_8bit: bool = False,
    use_fast_tokenizer: bool = True,
    trust_remote_code_tokenizer: bool = False,
    trust_remote_code_model: bool = False,
    revision: str = "main",
    model_max_length: int = None,
):
    """
    Returns an instance of the corresponding Answer Generator Model.
    Parameters
    ----------
    llm_name: str
        The model id, it could be a huggingface repo id, a ggml repo id, or an openai model id.
    llm_type: str
        The type of LLM to use.
    ggml_model_filename: str
        The filename of the model to load if using a ggml model
    use_cpu: bool
        Whether to use cpu or gpu
    model_config: str
        The filename of the model config to load if using a ggml model
    load_in_8bit: bool
        Whether to load the model in 8bit mode
    use_fast_tokenizer: bool
        Whether to use the fast tokenizer
    trust_remote_code_tokenizer: bool
        Whether to trust the remote code when loading the tokenizer
    trust_remote_code_model: bool
        Whether to trust the remote code when loading the model
    revision: str
        The specific model version to use. It can be a branch name, a tag name, or a commit id, since we use a git-based system for storing models
    model_max_length: int
        The maximum length of the model.
    Returns
    -------
    model:
        An instance of the corresponding LLM Model.
    """

    return LLM_CLASSES[llm_type](
        llm_name=llm_name,
        ggml_model_filename=ggml_model_filename,
        use_cpu=use_cpu,
        model_config=model_config,
        load_in_8bit=load_in_8bit,
        use_fast_tokenizer=use_fast_tokenizer,
        trust_remote_code_tokenizer=trust_remote_code_tokenizer,
        trust_remote_code_model=trust_remote_code_model,
        revision=revision,
        model_max_length=model_max_length,
    )


class RAGCacheOnWorkerTask(Task):
    CACHED_RAGS = {}

    def __init__(self):
        if is_celery_worker() and not self.CACHED_RAGS:
            self.CACHED_RAGS = self.preload_models()

    @staticmethod
    def preload_models():
        from chat_rag.inf_retrieval.embedding_models import E5Model
        from back.apps.language_model.retriever_clients import (
            ColBERTRetriever,
            PGVectorRetriever,
        )

        logger.info("Preloading models...")
        RAGConfig = apps.get_model("language_model", "RAGConfig")
        Embedding = apps.get_model("language_model", "Embedding")
        cache = {}

        for rag_conf in RAGConfig.enabled_objects.all():
            if Embedding.objects.filter(rag_config=rag_conf).exists():
                logger.info(
                    f"Loading RAG config: {rag_conf.name} "
                    f"with llm: {rag_conf.llm_config.llm_name} "
                    f"with llm type: {rag_conf.llm_config.llm_type} "
                    f"with knowledge base: {rag_conf.knowledge_base.name} "
                    f"with retriever: {rag_conf.retriever_config.model_name} "
                    f"and retriever device: {rag_conf.retriever_config.device}"
                )

                retriever_type = rag_conf.retriever_config.retriever_type

                if retriever_type == "colbert":
                    retriever = ColBERTRetriever.from_index(rag_conf)
                    rerank = False
                elif retriever_type == "e5":
                    hugginface_key = os.environ.get("HUGGINGFACE_KEY", None)

                    e5_model = E5Model(
                        model_name=rag_conf.retriever_config.model_name,
                        use_cpu=rag_conf.retriever_config.device == "cpu",
                        huggingface_key=hugginface_key,
                    )

                    retriever = PGVectorRetriever(
                        embedding_model=e5_model,
                        rag_config=rag_conf,
                    )
                    rerank = True
                else:
                    raise ValueError(f"Retriever type: {retriever_type} not supported.")

                llm_model = get_model(
                    llm_name=rag_conf.llm_config.llm_name,
                    llm_type=rag_conf.llm_config.llm_type,
                    ggml_model_filename=rag_conf.llm_config.ggml_llm_filename,
                    use_cpu=False,
                    model_config=rag_conf.llm_config.model_config,
                    load_in_8bit=rag_conf.llm_config.load_in_8bit,
                    use_fast_tokenizer=rag_conf.llm_config.use_fast_tokenizer,
                    trust_remote_code_tokenizer=rag_conf.llm_config.trust_remote_code_tokenizer,
                    trust_remote_code_model=rag_conf.llm_config.trust_remote_code_model,
                    revision=rag_conf.llm_config.revision,
                    model_max_length=rag_conf.llm_config.model_max_length,
                )

                cache[str(rag_conf.name)] = RAG(
                    retriever=retriever,
                    llm_model=llm_model,
                    lang=rag_conf.knowledge_base.lang,
                    rerank=rerank,
                )
                logger.info("...model loaded.")

            else:
                logger.info(f"RAG config: {rag_conf.name} needs to be indexed.")

        return cache


def _send_message(
    bot_channel_name,
    lm_msg_id,
    channel_layer,
    chanel_name,
    msg={},
    references={},
    final=False,
):
    async_to_sync(channel_layer.send)(
        chanel_name,
        {
            "type": "send_llm_response",
            "message": {
                "references": references,
                "final": final,
                "res": msg.get("res", ""),
                "bot_channel_name": bot_channel_name,
                "lm_msg_id": lm_msg_id,
            },
        },
    )


@app.task(bind=True, base=RAGCacheOnWorkerTask)
def llm_query_task(
    self,
    chanel_name=None,
    rag_config_name=None,
    input_text=None,
    conversation_id=None,
    bot_channel_name=None,
    recache_models=False,
    log_caller="None",
):
    logger.info(f"Log caller: {log_caller}")
    if recache_models:
        import torch
        # clear CACHED_RAGS
        torch.cuda.empty_cache()
        
        if hasattr(self, "CACHED_RAGS"):
            del self.CACHED_RAGS
        gc.collect()
        self.CACHED_RAGS = self.preload_models()
        return
    
    channel_layer = get_channel_layer()
    lm_msg_id = str(uuid.uuid4())

    RAGConfig = apps.get_model("language_model", "RAGConfig")
    Conversation = apps.get_model("broker", "Conversation")
    KnowledgeItem = apps.get_model("language_model", "KnowledgeItem")
    try:
        rag_conf = RAGConfig.enabled_objects.get(name=rag_config_name)
    except RAGConfig.DoesNotExist:
        logger.error(f"RAG config with name: {rag_config_name} does not exist.")
        _send_message(
            bot_channel_name, lm_msg_id, channel_layer, chanel_name, final=True
        )
        return

    logger.info("-" * 80)
    logger.info(f"Input query: {input_text}")

    p_conf = model_to_dict(rag_conf.prompt_config)
    g_conf = model_to_dict(rag_conf.generation_config)

    logger.info(f"Prompt config: {p_conf}")
    logger.info(f"Generation config: {g_conf}")

    # remove the ids
    p_conf.pop("id")
    g_conf.pop("id")
    # remove the tags and end tokens from the stop words
    stop_words = [
        p_conf["user_tag"],
        p_conf["assistant_tag"],
        p_conf["user_end"],
        p_conf["assistant_end"],
    ]
    # remove empty stop words
    stop_words = [word for word in stop_words if word]

    logger.info(f"Stop words: {stop_words}")

    # # Gatherings all the previous messages from the conversation
    prev_messages, human_messages_id = Conversation.objects.get(
        pk=conversation_id
    ).get_mml_chain(as_conv_format=True)

    prev_contents = list(
        KnowledgeItem.objects.filter(
            messageknowledgeitem__message_id__in=human_messages_id[
                :-1
            ]  # except current message
        )
        .distinct()
        .order_by("updated_date")
        .values_list("content", flat=True)
    )

    rag = self.CACHED_RAGS[rag_config_name]

    logger.info(f"Using RAG config: {rag_config_name}")

    streaming = True # TODO: make this a parameter
    reference_kis = []

    try:
        if streaming:
            for res in rag.stream(
                prev_messages,
                prev_contents,
                prompt_structure_dict=p_conf,
                generation_config_dict=g_conf,
                stop_words=stop_words,
            ):
                _send_message(
                    bot_channel_name, lm_msg_id, channel_layer, chanel_name, msg=res
                )
                reference_kis = res.get("context")
        else:
            res = rag.generate(
                prev_messages,
                prompt_structure_dict=p_conf,
                generation_config_dict=g_conf,
                stop_words=stop_words,
            )
            _send_message(bot_channel_name, lm_msg_id, channel_layer, chanel_name, msg=res)
            reference_kis = res.get("context")

    except Exception as e:
        logger.error("Prompt too long.")
        _send_message(
            bot_channel_name, lm_msg_id, channel_layer, chanel_name, final=True, msg={"res": e.message}
        )
        return

    reference_kis = reference_kis[0] if len(reference_kis) > 0 else []
    logger.info(f"\nReferences: {reference_kis}")
    print(
        {
            "knowledge_base_id": rag_conf.knowledge_base.pk,
            "knowledge_items": reference_kis,
        }
    )
    _send_message(
        bot_channel_name,
        lm_msg_id,
        channel_layer,
        chanel_name,
        references={
            "knowledge_base_id": rag_conf.knowledge_base.pk,
            "knowledge_items": reference_kis
        },
        final=True,
    )

    MessageKnowledgeItem = apps.get_model("language_model", "MessageKnowledgeItem")
    Message = apps.get_model("broker", "Message")
    # get the last message from the conversation
    last_message = (
        Message.objects.filter(
            conversation_id=conversation_id, sender__contains={"type": "human"}
        )
        .order_by("-created_date")
        .first()
    )

    MessageKnowledgeItem.objects.bulk_create(
        [
            MessageKnowledgeItem(
                message=last_message,
                knowledge_item_id=ki["knowledge_item_id"],
                similarity=ki["similarity"],
            )
            for ki in reference_kis
        ]
    )


def get_modified_k_items_ids(rag_config):
    """
    Get the ids of the k items that have been modified.
    Parameters
    ----------
    rag_config : RAGConfig
        The RAGConfig object.
    Returns
    -------
    modified_k_item_ids : list
        A list of primary keys of the KnowledgeItem objects.
    """
    Embedding = apps.get_model("language_model", "Embedding")

    modified_k_item_ids = list(
        Embedding.objects.filter(
            rag_config=rag_config,
            updated_date__lt=F("knowledge_item__updated_date"),
        ).values_list("knowledge_item__pk", flat=True)
    )

    return modified_k_item_ids


def generate_embeddings(k_items, rag_config):
    """
    Generate the embeddings for a knowledge base.
    Parameters
    ----------
    ki_ids : list
        A list of primary keys of the KnowledgeItem objects.
    ragconfig_id : int
        The primary key of the RAGConfig object.
    """

    from chat_rag.inf_retrieval.embedding_models import E5Model

    Embedding = apps.get_model("language_model", "Embedding")

    model_name = rag_config.retriever_config.model_name
    batch_size = rag_config.retriever_config.batch_size
    device = rag_config.retriever_config.device

    logger.info(
        f"Generating embeddings for {k_items.count()} knowledge items. Knowledge base: {rag_config.knowledge_base.name}"
    )
    logger.info(f"Retriever model: {model_name}")
    logger.info(f"Batch size: {batch_size}")
    logger.info(f"Device: {device}")

    embedding_model = E5Model(
        model_name=model_name,
        use_cpu=device == "cpu",
        huggingface_key=os.environ.get("HUGGINGFACE_KEY", None),
    )

    contents = [item.content for item in k_items]
    embeddings = embedding_model.build_embeddings(
        contents=contents, batch_size=batch_size
    )

    # from tensor to list
    embeddings = [embedding.tolist() for embedding in embeddings]

    new_embeddings = [
        Embedding(
            knowledge_item=item,
            rag_config=rag_config,
            embedding=embedding,
        )
        for item, embedding in zip(k_items, embeddings)
    ]

    Embedding.objects.bulk_create(new_embeddings)
    logger.info(
        f"Embeddings generated for knowledge base: {rag_config.knowledge_base.name}"
    )


def index_e5(rag_config, caller: str = None):
    """
    Generate the embeddings for a knowledge base for the E5 retriever.
    Parameters
    ----------
    rag_config_id : int
        The primary key of the RAGConfig object.
    """
    KnowledgeItem = apps.get_model("language_model", "KnowledgeItem")
    Embedding = apps.get_model("language_model", "Embedding")

    # When a k item is deleted, its embedding is also deleted in cascade, so we need to remove the embeddings of only the modified k items
    # get the modified k items ids
    modified_k_item_ids = get_modified_k_items_ids(rag_config)

    logger.info(f"Number of modified k items: {len(modified_k_item_ids)}")

    # remove the embeddings of the modified k items
    Embedding.objects.filter(knowledge_item__pk__in=modified_k_item_ids).delete()

    # get the k items that have no associated embeddings
    k_items = KnowledgeItem.objects.filter(
        knowledge_base=rag_config.knowledge_base
    ).exclude(embedding__rag_config=rag_config)

    generate_embeddings(k_items=k_items, rag_config=rag_config)


def modify_index(rag_config):
    """
    Modify the index for a knowledge base. It removes, modifies and adds the k items to an existing index.
    Parameters
    ----------
    rag_config_id : int
        The primary key of the RAGConfig object.
    """

    from back.apps.language_model.retriever_clients import ColBERTRetriever


    KnowledgeItem = apps.get_model("language_model", "KnowledgeItem")
    Embedding = apps.get_model("language_model", "Embedding")

    retriever = ColBERTRetriever.from_index(rag_config=rag_config)

    # k items to remove
    current_k_item_ids = KnowledgeItem.objects.filter(
        knowledge_base=rag_config.knowledge_base
    ).values_list("pk", flat=True)

    indexed_k_item_ids = [
        int(id) for id in retriever.retriever.model.docid_pid_map.keys()
    ]

    # Current indexed k items - k items in the database = k items to remove
    k_item_ids_to_remove = set(indexed_k_item_ids) - set(current_k_item_ids)

    logger.info(f"Number of k items to remove: {len(k_item_ids_to_remove)}")

    # modified k items need to be removed from the index also, to detect which k items are modified we check if the k_item embedding updated_date is lower than the k_item updated_date
    modified_k_item_ids = get_modified_k_items_ids(rag_config)

    logger.info(f"Number of modified k items: {len(modified_k_item_ids)}")

    # add the modified k items to the k items to remove
    k_item_ids_to_remove = k_item_ids_to_remove.union(modified_k_item_ids)

    # ids to string
    k_item_ids_to_remove = [str(id) for id in k_item_ids_to_remove]

    if len(k_item_ids_to_remove) > 0:
        # remove the k items from the ColBERT index
        retriever.delete_from_index(
            rag_config=rag_config, k_item_ids=k_item_ids_to_remove
        )

    # remove the embeddings with the given ids
    Embedding.objects.filter(knowledge_item__pk__in=k_item_ids_to_remove).delete()

    # get the k items that have no associated embeddings
    k_items = KnowledgeItem.objects.filter(
        knowledge_base=rag_config.knowledge_base
    ).exclude(embedding__rag_config=rag_config)

    logger.info(f"Number of k items to add: {len(k_items)}")

    if k_items.count() > 0:
        # add the k items to the ColBERT index
        try:
            retriever.add_to_index(rag_config=rag_config, k_items=k_items)

            # create an empty embedding for each knowledge item for the given rag config for tracking which items are indexed
            embeddings = [
                Embedding(
                    knowledge_item=item,
                    rag_config=rag_config,
                )
                for item in k_items
            ]
            Embedding.objects.bulk_create(embeddings)

        except Exception as e:
            logger.error(f"Error adding k items to index: {e}")
            logger.info(
                "This error is probably due to too few knowledge items to add to the index."
            )
            logger.info("Rebuilding index from scratch...")
            # remove all embeddings for the given rag config
            Embedding.objects.filter(rag_config=rag_config).delete()
            # indexing starting from scratch
            creates_index(rag_config=rag_config)


def creates_index(rag_config, caller: str = None):
    """
    Build the index for a knowledge base.
    Parameters
    ----------
    rag_config_id : int
        The primary key of the RAGConfig object.
    """

    from back.apps.language_model.retriever_clients import ColBERTRetriever

    logger.info(f"Log caller: {caller}")

    Embedding = apps.get_model("language_model", "Embedding")
    KnowledgeItem = apps.get_model("language_model", "KnowledgeItem")

    k_items = KnowledgeItem.objects.filter(knowledge_base=rag_config.knowledge_base)

    index_path = ColBERTRetriever.index(rag_config=rag_config, k_items=k_items)
    # create an empty embedding for each knowledge item for the given rag config for tracking which items are indexed
    embeddings = [
        Embedding(
            knowledge_item=item,
            rag_config=rag_config,
        )
        for item in k_items
    ]
    Embedding.objects.bulk_create(embeddings)


def index_colbert(rag_config, caller: str = None):
    """
    Build the index for a knowledge base.
    Parameters
    ----------
    rag_config_id : int
        The primary key of the RAGConfig object.
    """

    Embedding = apps.get_model("language_model", "Embedding")

    if Embedding.objects.filter(
        rag_config=rag_config
    ).exists():  # if there are embeddings for the given rag config
        modify_index(rag_config)

    else:
        creates_index(rag_config=rag_config, caller=caller)


@app.task()
def index_task(rag_config_id, recache_models: bool = False, caller: str = None):
    """
    Build the index for a knowledge base.
    Parameters
    ----------
    rag_config_id : int
        The primary key of the RAGConfig object.
    """
    RAGConfig = apps.get_model("language_model", "RAGConfig")
    rag_config = RAGConfig.objects.get(pk=rag_config_id)

    retriever_type = rag_config.retriever_config.retriever_type

    if retriever_type == "e5":
        index_e5(rag_config, caller=caller)
    elif retriever_type == "colbert":
        index_colbert(rag_config, caller=caller)

    rag_config.index_up_to_date = True
    rag_config.save()

    logger.info(f"Index built for knowledge base: {rag_config.knowledge_base.name}")
    if recache_models:
        recache_models_utils(log_caller=caller)


@app.task()
def delete_index_files_task(s3_index_path, recache_models: bool = False):
    """
    Delete the index files from S3.
    Parameters
    ----------
    s3_index_path : str
        The unique index path.
    """
    from django.core.files.storage import default_storage

    if s3_index_path:
        logger.info(f"Deleting index files from S3: {s3_index_path}")
        # List all files in the unique index path
        _, files = default_storage.listdir(s3_index_path)
        for file in files:
            # Construct the full path for each file
            file_path = os.path.join(s3_index_path, file)
            # Delete the file from S3
            default_storage.delete(file_path)

        logger.info(f"Index files deleted from S3: {s3_index_path}")

        if recache_models:
            recache_models_utils()


@app.task()
def parse_url_task(ds_id, url):
    """
    Get the html from the url and parse it.
    Parameters
    ----------
    ds_id : int
        The primary key of the data source to which the crawled items will be added.
    url : str
        The url to crawl.
    """
    from back.apps.language_model.scraping.scraping.spiders.generic import (
        GenericSpider,
    )  # CI

    runner = CrawlerRunner(get_project_settings())
    runner.crawl(GenericSpider, start_urls=url, data_source_id=ds_id)
    KnowledgeBase = apps.get_model("language_model", "KnowledgeBase")
    kb = KnowledgeBase.objects.get(pk=ds_id)


@app.task()
def parse_pdf_task(ds_pk):
    """
    Parse a pdf file and return a list of KnowledgeItem objects.
    Parameters
    ----------
    ds_pk : int
        The primary key of the data source to parse.
    Returns
    -------
    k_items : list
        A list of KnowledgeItem objects.
    """
    from chat_rag.data.splitters import get_splitter
    from chat_rag.data.parsers import parse_pdf

    logger.info("Parsing PDF file...")
    logger.info(f"PDF file pk: {ds_pk}")

    DataSource = apps.get_model("language_model", "DataSource")
    KnowledgeItem = apps.get_model("language_model", "KnowledgeItem")
    KnowledgeItemImage = apps.get_model("language_model", "KnowledgeItemImage")
    ds = DataSource.objects.get(pk=ds_pk)
    pdf_file = ds.original_pdf.read()
    strategy = ds.strategy
    splitter = ds.splitter
    chunk_size = ds.chunk_size
    chunk_overlap = ds.chunk_overlap

    pdf_file = BytesIO(pdf_file)

    splitter = get_splitter(splitter, chunk_size, chunk_overlap)

    logger.info(f"Splitter: {splitter}")
    logger.info(f"Strategy: {strategy}")
    logger.info(f"Chunk size: {chunk_size}")
    logger.info(f"Chunk overlap: {chunk_overlap}")

    parsed_items = parse_pdf(file=pdf_file, strategy=strategy, split_function=splitter)

    with transaction.atomic():
        for item in parsed_items:
            # Create and save the KnowledgeItem instance
            knowledge_item = KnowledgeItem(
                knowledge_base=ds.knowledge_base,
                data_source=ds,
                title=item.title,
                content=item.content,  # alnaf [[Image 0]] a;mda [[Image 2]]
                url=item.url,
                section=item.section,
                page_number=item.page_number,
                metadata=item.metadata,
            )
            knowledge_item.save()

            # For each image in the item, create and save a KnowledgeItemImage instance
            if item.images:
                for index, image in item.images.items():
                    image_instance = KnowledgeItemImage(
                        image_base64=image.image_base64,
                        knowledge_item=knowledge_item,
                        image_caption=image.image_caption,
                    )
                    image_instance.save()

                    # If the image does not have a caption, use a default caption
                    image_caption = (
                        image.image_caption if image.image_caption else f"Image {index}"
                    )

                    # Replace the placeholder image with the actual image markdown
                    knowledge_item.content = knowledge_item.content.replace(
                        f"[[Image {index}]]",
                        f"![{image_caption}]({image_instance.image_file.name})",
                    )
                    knowledge_item.save()

@app.task()
def generate_titles(knowledge_base_pk, n_titles=10):
    """
    Generate titles for the knowledge items of a knowledge base.
    Parameters
    ----------
    knowledge_base_pk : int
        The primary key of the knowledge base.
    n_titles : int
        The number of titles to generate for each knowledge item.
    """
    from tqdm import tqdm
    from chat_rag.inf_retrieval.query_generator import QueryGenerator

    KnowledgeItem = apps.get_model("language_model", "KnowledgeItem")
    AutoGeneratedTitle = apps.get_model("language_model", "AutoGeneratedTitle")

    kb = KnowledgeItem.objects.filter(knowledge_base=knowledge_base_pk)

    logger.info(f"Generating titles for {kb.count()} knowledge items")
    for item in tqdm(kb):
        queries = QueryGenerator(settings.OPENAI_API_KEY)(item.content, n_titles)
        new_titles = [
            AutoGeneratedTitle(
                knowledge_item=item,
                title=title,
            )
            for title in queries
        ]
        AutoGeneratedTitle.objects.bulk_create(new_titles)

    logger.info(f"Titles generated for knowledge base: {kb[0].knowledge_base.name}")


def get_similarity_scores(titles, retriever):
    """
    Get the similarity scores for a list of titles.
    Parameters
    ----------
    titles : list
        A list of titles.
    retriever : PGVectorRetriever
        The retriever to use.
    Returns
    -------
    mean_similarity : float
        The mean similarity score.
    std_similarity : float
        The standard deviation of the similarity scores.
    """
    import numpy as np

    results = retriever.retrieve(titles, top_k=1)
    similarities = [item[0]["similarity"] for item in results]
    mean_similarity = np.mean(similarities)
    std_similarity = np.std(similarities)

    return mean_similarity, std_similarity


@app.task()
def generate_suggested_intents_task(knowledge_base_pk):
    """
    Generate new intents from the users' queries.
    Parameters
    ----------
    knowledge_base_pk : int
        The primary key of the knowledge base.
    """

    from chat_rag.inf_retrieval.embedding_models import E5Model
    from chat_rag.intent_detection import clusterize_text, generate_intents
    from django.db.models import Max
    from back.apps.language_model.retriever_clients import PGVectorRetriever
    from back.apps.language_model.prompt_templates import get_queries_out_of_domain

    logger.info("generate_new_intents_task called")

    RAGConfig = apps.get_model("language_model", "RAGConfig")
    MessageKnowledgeItem = apps.get_model("language_model", "MessageKnowledgeItem")
    Message = apps.get_model("broker", "Message")
    AutoGeneratedTitle = apps.get_model("language_model", "AutoGeneratedTitle")
    Intent = apps.get_model("language_model", "Intent")

    hugginface_key = os.environ.get("HUGGINGFACE_KEY", None)

    # These are in domain titles
    titles_in_domain = AutoGeneratedTitle.objects.filter(
        knowledge_item__knowledge_base=knowledge_base_pk
    )[:100]

    # Get the RAG config that corresponds to the knowledge base
    rag_conf = RAGConfig.objects.filter(knowledge_base=knowledge_base_pk).first()
    lang = rag_conf.knowledge_base.lang

    # if the retriever type is not e5, then return
    if rag_conf.retriever_config.retriever_type != "e5":
        logger.info(f"Intent generation is not supported for retriever type: {rag_conf.retriever_config.retriever_type} right now")
        return

    e5_model = E5Model(
        model_name=rag_conf.retriever_config.model_name,
        use_cpu=rag_conf.retriever_config.device == "cpu",
        huggingface_key=hugginface_key,
    )

    retriever = PGVectorRetriever(
        embedding_model=e5_model,
        rag_config=rag_conf,
    )

    # Get similarity scores for the in domain titles and the out of domain queries
    mean_sim_in_domain, std_sim_in_domain = get_similarity_scores(
        [title.title for title in titles_in_domain], retriever
    )

    mean_sim_out_domain, std_sim_out_domain = get_similarity_scores(
        get_queries_out_of_domain(lang), retriever
    )

    logger.info(
        f"Mean similarity in domain: {mean_sim_in_domain}, std: {std_sim_in_domain}"
    )
    logger.info(
        f"Mean similarity out domain: {mean_sim_out_domain}, std: {std_sim_out_domain}"
    )

    # The suggested new intents will have a similarity score between the in domain queries and the out of domain queries
    new_intents_thresholds = {
        "max": mean_sim_in_domain - std_sim_in_domain,
        "min": mean_sim_out_domain + std_sim_out_domain,
    }

    logger.info(f"Suggested intents thresholds: {new_intents_thresholds}")

    # check that the max is greater than the min
    if new_intents_thresholds["max"] < new_intents_thresholds["min"]:
        logger.info(
            "Max threshold is lower than min threshold, no new intents will be generated"
        )
        return

    messages = MessageKnowledgeItem.objects.values("message_id").annotate(
        max_similarity=Max("similarity")
    )

    logger.info(f"Number of messages: {messages.count()}")

    # filter the results if the max similarity is between the thresholds
    messages = messages.filter(
        max_similarity__lte=new_intents_thresholds["max"],
        max_similarity__gte=new_intents_thresholds["min"],
    )

    logger.info(f"Number of messages after filtering: {messages.count()}")

    if messages.count() == 0:
        logger.info("There are no suggested intents to generate")
        return

    messages_text = [
        Message.objects.get(id=item["message_id"]).stack[0]["payload"]
        for item in messages
    ]

    # get the cluster labels
    labels = clusterize_text(
        messages_text,
        e5_model,
        batch_size=rag_conf.retriever_config.batch_size,
        prefix="query: ",
    )
    k_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    logger.info(f"Number of clusters: {k_clusters}")

    # list of lists of queries associated to each cluster
    clusters = [[] for _ in range(k_clusters)]
    cluster_instances = [[] for _ in range(k_clusters)]
    for label, query, message_instace in zip(labels, messages_text, messages):
        if label != -1:  # -1 is the label for outliers
            clusters[label].append(query)
            cluster_instances[label].append(message_instace)

    # generate the intents
    intents = generate_intents(clusters)

    # save the intents
    new_intents = [
        Intent(
            intent_name=intent,
            auto_generated=True,
            valid=False,
            suggested_intent=True,
        )
        for intent in intents
    ]

    Intent.objects.bulk_create(new_intents)

    logger.info(f"Number of new intents: {len(new_intents)}")

    # add the messages to each intent
    for intent_cluster, intent in zip(cluster_instances, new_intents):
        # get the value of key 'message_id' from each message
        intent_cluster = [item["message_id"] for item in intent_cluster]
        intent.message.add(*intent_cluster)

    logger.info("New intents generated successfully")


@app.task()
def generate_intents_task(knowledge_base_pk):
    """
    Generate existing intents from a knowledge base.
    Parameters
    ----------
    knowledge_base_pk : int
        The primary key of the knowledge base.
    """
    from chat_rag.inf_retrieval.embedding_models import E5Model
    from chat_rag.intent_detection import clusterize_text, generate_intents
    from back.apps.language_model.models import AutoGeneratedTitle
    KnowledgeItem = apps.get_model("language_model", "KnowledgeItem")

    Intent = apps.get_model("language_model", "Intent")
    RAGConfig = apps.get_model("language_model", "RAGConfig")
    rag_conf = RAGConfig.objects.filter(knowledge_base=knowledge_base_pk).first()

    # if the retriever type is not e5, then return
    if rag_conf.retriever_config.retriever_type != "e5":
        logger.info(f"Intent generation is not supported for retriever type: {rag_conf.retriever_config.retriever_type} right now")
        return

    hugginface_key = os.environ.get("HUGGINGFACE_KEY", None)

    e5_model = E5Model(
        model_name=rag_conf.retriever_config.model_name,
        use_cpu=rag_conf.retriever_config.device == "cpu",
        huggingface_key=hugginface_key,
    )
    # AutoGeneratedTitle = apps.get_model("language_model", "AutoGeneratedTitle")

    k_items = KnowledgeItem.objects.filter(knowledge_base=knowledge_base_pk)

    logger.info(f"Generating intents for {k_items.count()} knowledge items")

    # These are in domain titles
    autogen_titles = AutoGeneratedTitle.objects.filter(
        knowledge_item__knowledge_base=knowledge_base_pk
    )

    # get as maximum 10 autogen_titles per knowledge item
    final_autogen_titles = []
    for item in k_items:
        titles = autogen_titles.filter(knowledge_item=item)[:10]
        final_autogen_titles.extend(titles)

    logger.info(f"Number of titles: {len(final_autogen_titles)}")

    # get the queries
    queries = [title.title for title in final_autogen_titles]

    # clusterize the queries
    logger.info("Clusterizing queries...")
    labels = clusterize_text(
        queries,
        e5_model,
        batch_size=rag_conf.retriever_config.batch_size,
        prefix="query: ",
    )
    k_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    logger.info(f"Number of clusters: {k_clusters}")

    # list of lists of queries associated to each cluster
    clusters = [[] for _ in range(k_clusters)]
    cluster_instances = [[] for _ in range(k_clusters)]
    for label, query, title_instance in zip(labels, queries, final_autogen_titles):
        if label != -1:  # -1 is the label for outliers
            clusters[label].append(query)
            cluster_instances[label].append(title_instance)

    # generate the intents
    intents = generate_intents(clusters)

    logger.info(f"Number of new intents: {len(intents)} generated")

    # save the intents
    new_intents = [
        Intent(
            intent_name=intent,
            auto_generated=True,
            valid=False,
            suggested_intent=False,
        )
        for intent in intents
    ]

    Intent.objects.bulk_create(new_intents)

    logger.info("Suggested intents saved successfully")

    # add the knowledge items to each intent
    for intent_cluster, intent in zip(cluster_instances, new_intents):
        # get the knowledge items from each title
        intent_cluster = [item.knowledge_item for item in intent_cluster]
        # remove duplicated knowledge items
        intent_cluster = list(set(intent_cluster))
        intent.knowledge_item.add(*intent_cluster)

    logger.info("Knowledge items added to the intents successfully")
