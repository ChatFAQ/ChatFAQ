import uuid
from io import StringIO, BytesIO
from logging import getLogger
from asgiref.sync import async_to_sync
from celery import Task
from channels.layers import get_channel_layer
from chatfaq_retrieval import RetrieverAnswerer
from chatfaq_retrieval.models import GGMLModel, HFModel, OpenAIModel, VLLModel
from chatfaq_retrieval.data.splitters import get_splitter
from chatfaq_retrieval.data.parsers import parse_pdf
from scrapy.utils.project import get_project_settings
from django.apps import apps
from back.config.celery import app
from back.utils import is_celery_worker
from django.forms.models import model_to_dict
from scrapy.crawler import CrawlerRunner
from crochet import setup

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
    )


class RAGCacheOnWorkerTask(Task):
    CACHED_RAGS = {}

    def __init__(self):
        if is_celery_worker() and not self.CACHED_RAGS:
            self.CACHED_RAGS = self.preload_models()

    @staticmethod
    def preload_models():
        print("Preloading models...")
        RAGConfig = apps.get_model('language_model', 'RAGConfig')
        cache = {}
        for rag_conf in RAGConfig.objects.all():
            print(
                f"Loading RAG config: {rag_conf.name} "
                f"with model: {rag_conf.llm_config.name} "
                f"and knowledge base: {rag_conf.knowledge_base.name}"
            )
            cache[str(rag_conf.name)] = RetrieverAnswerer(
                base_data=StringIO(rag_conf.knowledge_base.to_csv()),
                llm_name=rag_conf.llm_config.llm_name,
                context_col="content",
                embedding_col="content",
                use_cpu=False,
                retriever_model=rag_conf.retriever_model,
                llm_model=get_model(
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
                ),
            )
            print("...model loaded.")
        return cache


msg_template = {
    "context": None,
    "final": False,
    "res": "",
}


def _send_message(bot_channel_name, lm_msg_id, channel_layer, chanel_name, msg={}, final=False):
    msg_template["bot_channel_name"] = bot_channel_name
    msg_template["lm_msg_id"] = lm_msg_id
    if not msg_template["context"] and msg.get("context"):
        msg_template["context"] = msg["context"]
    msg_template["res"] = msg.get("res", "")
    msg_template["final"] = final

    async_to_sync(channel_layer.send)(
        chanel_name,
        {
            "type": "send_llm_response",
            "message": msg_template,
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
    recache_models=False
):
    if recache_models:
        self.CACHED_RAGS = self.preload_models()
        return
    channel_layer = get_channel_layer()
    lm_msg_id = str(uuid.uuid4())

    RAGConfig = apps.get_model('language_model', 'RAGConfig')
    try:
        rag_conf = RAGConfig.objects.get(name=rag_config_name)
    except RAGConfig.DoesNotExist:
        logger.error(f"RAG config with name: {rag_config_name} does not exist.")
        _send_message(bot_channel_name, lm_msg_id, channel_layer, chanel_name, final=True)
        return

    p_conf = model_to_dict(rag_conf.prompt_config)
    g_conf = model_to_dict(rag_conf.generation_config)

    # remove the ids
    p_conf.pop("id")
    g_conf.pop("id")
    # remove the tags and end tokens from the stop words
    stop_words = [p_conf["user_tag"], p_conf["assistant_tag"], p_conf["user_end"], p_conf["assistant_end"]]
    # remove empty stop words
    stop_words = [word for word in stop_words if word]

    # # Gatherings all the previous messages from the conversation
    # prev_messages = Conversation.objects.get(pk=conversation_id).get_mml_chain()

    rag = self.CACHED_RAGS[rag_config_name]
    streaming = True
    if streaming:
        for res in rag.stream(
            input_text,
            prompt_structure_dict=p_conf,
            generation_config_dict=g_conf,
            stop_words=stop_words,
            lang=rag_conf.knowledge_base.lang,
        ):
            _send_message(bot_channel_name, lm_msg_id, channel_layer, chanel_name, msg=res)
    else:
        res = rag.generate(
            input_text,
            prompt_structure_dict=p_conf,
            generation_config_dict=g_conf,
            stop_words=stop_words,
            lang=rag_conf.knowledge_base.lang,
        )
        _send_message(bot_channel_name, lm_msg_id, channel_layer, chanel_name, msg=res)

    _send_message(bot_channel_name, lm_msg_id, channel_layer, chanel_name, final=True)


@app.task()
def parse_url_task(knowledge_base_id, url):
    """
    Get the html from the url and parse it.
    Parameters
    ----------
    dataset_id : int
        The primary key of the dataset to which the crawled items will be added.
    url : str
        The url to crawl.
    """
    from back.apps.language_model.scraping.scraping.spiders.generic import GenericSpider  # CI
    runner = CrawlerRunner(get_project_settings())
    runner.crawl(GenericSpider, start_urls=url, knowledge_base_id=knowledge_base_id)


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

    KnowledgeBase = apps.get_model('language_model', 'KnowledgeBase')
    kb = KnowledgeBase.objects.get(pk=pdf_file_pk)
    pdf_file = kb.original_pdf.read()
    strategy = kb.strategy
    splitter = kb.splitter
    chunk_size = kb.chunk_size
    chunk_overlap = kb.chunk_overlap

    pdf_file = BytesIO(pdf_file)

    splitter = get_splitter(splitter, chunk_size, chunk_overlap)

    k_items = parse_pdf(file=pdf_file, strategy=strategy, split_function=splitter)

    KnowledgeItem = apps.get_model('language_model', 'KnowledgeItem')

    new_items = [
            KnowledgeItem(
                dataset=kb,
                title=k_item.title,
                content=k_item.content,
                url=k_item.url,
                section=k_item.section,
                page_number=k_item.page_number
            )
            for k_item in k_items
        ]

    KnowledgeItem.objects.filter(dataset=pdf_file_pk).delete() # TODO: give the option to reset the dataset or not, if reset is True, pass the last date of the last item to the spider and delete them when the crawling finisges
    KnowledgeItem.objects.bulk_create(new_items)


