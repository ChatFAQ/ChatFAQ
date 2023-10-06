import uuid
from io import BytesIO
from logging import getLogger
from asgiref.sync import async_to_sync
from celery import Task
from channels.layers import get_channel_layer
from chat_rag import RAG
from chat_rag.llms import GGMLModel, HFModel, OpenAIModel, VLLModel
from chat_rag.inf_retrieval.embedding_models import E5Model
from chat_rag.inf_retrieval.retrievers import SemanticRetriever
from chat_rag.data.splitters import get_splitter
from chat_rag.data.parsers import parse_pdf
from scrapy.utils.project import get_project_settings
from django.apps import apps
from back.config.celery import app
from back.utils import is_celery_worker
from django.forms.models import model_to_dict
from scrapy.crawler import CrawlerRunner
from crochet import setup
import numpy as np
import os

if is_celery_worker():
    setup()

logger = getLogger(__name__)

LLM_CLASSES = {
    "local_cpu": GGMLModel,
    "local_gpu": HFModel,
    "vllm": VLLModel,
    "openai": OpenAIModel,
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
        The model id, it could be a hugginface repo id, a ggml repo id, or an openai model id.
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
        from back.apps.language_model.retriever_clients import PGVectorRetriever

        logger.info("Preloading models...")
        RAGConfig = apps.get_model("language_model", "RAGConfig")
        cache = {}
        for rag_conf in RAGConfig.objects.all():
            logger.info(
                f"Loading RAG config: {rag_conf.name} "
                f"with llm: {rag_conf.llm_config.llm_name} "
                f"with llm type: {rag_conf.llm_config.llm_type}"
                f"with knowledge base: {rag_conf.knowledge_base.name}"
                f"with retriever: {rag_conf.retriever_config.model_name}"
                f"and retriever device: {rag_conf.retriever_config.device}"
            )

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
            )
            logger.info("...model loaded.")

        return cache


def _send_message(
    bot_channel_name,
    lm_msg_id,
    channel_layer,
    chanel_name,
    msg={},
    references=[],
    final=False,
):
    async_to_sync(channel_layer.send)(
        chanel_name,
        {
            "type": "send_llm_response",
            "message": {
                "context": references,
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
        self.CACHED_RAGS = self.preload_models()
        return
    channel_layer = get_channel_layer()
    lm_msg_id = str(uuid.uuid4())

    RAGConfig = apps.get_model("language_model", "RAGConfig")
    try:
        rag_conf = RAGConfig.objects.get(name=rag_config_name)
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
    # prev_messages = Conversation.objects.get(pk=conversation_id).get_mml_chain()

    rag = self.CACHED_RAGS[rag_config_name]

    logger.info(f"Using RAG config: {rag_config_name}")

    streaming = True
    references = []
    if streaming:
        for res in rag.stream(
            input_text,
            prompt_structure_dict=p_conf,
            generation_config_dict=g_conf,
            stop_words=stop_words,
            lang=rag_conf.knowledge_base.lang,
        ):
            _send_message(
                bot_channel_name, lm_msg_id, channel_layer, chanel_name, msg=res
            )
            references = res.get("context")[0] # just the first context because it is only one query
    else:
        res = rag.generate(
            input_text,
            prompt_structure_dict=p_conf,
            generation_config_dict=g_conf,
            stop_words=stop_words,
            lang=rag_conf.knowledge_base.lang,
        )
        _send_message(bot_channel_name, lm_msg_id, channel_layer, chanel_name, msg=res)
        references = res.get("context")[0] # just the first context because it is only one query

    logger.info(f"\nReferences: {references}")
    _send_message(
        bot_channel_name,
        lm_msg_id,
        channel_layer,
        chanel_name,
        references=references,
        final=True,
    )


@app.task()
def generate_embeddings_task(ki_ids, rag_config_id, recache_models=False):
    """
    Generate the embeddings for a knowledge base.
    Parameters
    ----------
    ragconfig : int
        The primary key of the RAGConfig object.
    """
    KnowledgeItem = apps.get_model("language_model", "KnowledgeItem")
    RAGConfig = apps.get_model("language_model", "RAGConfig")
    ki_qs = KnowledgeItem.objects.filter(pk__in=ki_ids)
    rag_config = RAGConfig.objects.get(pk=rag_config_id)

    model_name = rag_config.retriever_config.model_name
    batch_size = rag_config.retriever_config.batch_size
    device = rag_config.retriever_config.device

    logger.info(
        f"Generating embeddings for {ki_qs.count()} knowledge items. Knowledge base: {rag_config.knowledge_base.name}"
    )
    logger.info(f"Retriever model: {model_name}")
    logger.info(f"Batch size: {batch_size}")
    logger.info(f"Device: {device}")

    embedding_model = E5Model(
            model_name=model_name,
            use_cpu=device == "cpu",
            huggingface_key=os.environ.get("HUGGINGFACE_KEY", None),
    )

    contents = [item.content for item in ki_qs]
    embeddings = embedding_model.build_embeddings(contents=contents, batch_size=batch_size)

    # from tensor to list
    embeddings = [embedding.tolist() for embedding in embeddings]

    Embedding = apps.get_model("language_model", "Embedding")
    new_embeddings = [
        Embedding(
            knowledge_item=item,
            rag_config=rag_config,
            embedding=embedding,
        )
        for item, embedding in zip(ki_qs, embeddings)
    ]

    Embedding.objects.bulk_create(new_embeddings)
    print(f"Embeddings generated for knowledge base: {rag_config.knowledge_base.name}")
    if recache_models:
        llm_query_task.delay(recache_models=True, log_caller="generate_embeddings_task")


@app.task()
def parse_url_task(knowledge_base_id, url):
    """
    Get the html from the url and parse it.
    Parameters
    ----------
    knowledge_base_id : int
        The primary key of the knowledge base to which the crawled items will be added.
    url : str
        The url to crawl.
    """
    from back.apps.language_model.scraping.scraping.spiders.generic import (
        GenericSpider,
    )  # CI

    runner = CrawlerRunner(get_project_settings())
    runner.crawl(GenericSpider, start_urls=url, knowledge_base_id=knowledge_base_id)
    KnowledgeBase = apps.get_model("language_model", "KnowledgeBase")
    kb = KnowledgeBase.objects.get(pk=knowledge_base_id)
    kb.trigger_generate_embeddings()


@app.task()
def parse_pdf_task(pdf_file_pk):
    """
    Parse a pdf file and return a list of KnowledgeItem objects.
    Parameters
    ----------
    pdf_file_pk : int
        The primary key of the pdf file to parse.
    Returns
    -------
    k_items : list
        A list of KnowledgeItem objects.
    """

    logger.info("Parsing PDF file...")
    logger.info(f"PDF file pk: {pdf_file_pk}")

    KnowledgeBase = apps.get_model("language_model", "KnowledgeBase")
    kb = KnowledgeBase.objects.get(pk=pdf_file_pk)
    pdf_file = kb.original_pdf.read()
    strategy = kb.strategy
    splitter = kb.splitter
    chunk_size = kb.chunk_size
    chunk_overlap = kb.chunk_overlap

    pdf_file = BytesIO(pdf_file)

    splitter = get_splitter(splitter, chunk_size, chunk_overlap)

    logger.info(f"Splitter: {splitter}")
    logger.info(f"Strategy: {strategy}")
    logger.info(f"Chunk size: {chunk_size}")
    logger.info(f"Chunk overlap: {chunk_overlap}")

    k_items = parse_pdf(file=pdf_file, strategy=strategy, split_function=splitter)

    KnowledgeItem = apps.get_model("language_model", "KnowledgeItem")

    new_items = [
        KnowledgeItem(
            knowledge_base=kb,
            title=k_item.title,
            content=k_item.content,
            url=k_item.url,
            section=k_item.section,
            page_number=k_item.page_number,
        )
        for k_item in k_items
    ]

    logger.info(f"Number of new items: {len(new_items)}")

    KnowledgeItem.objects.filter(
        knowledge_base=pdf_file_pk
    ).delete()  # TODO: give the option to reset the knowledge_base or not, if reset is True, pass the last date of the last item to the spider and delete them when the crawling finisges
    KnowledgeItem.objects.bulk_create(new_items)
    kb.trigger_generate_embeddings()
