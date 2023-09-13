import uuid
from io import StringIO
from logging import getLogger
from twisted.internet import reactor
from asgiref.sync import async_to_sync
from celery import Task
from channels.layers import get_channel_layer
from chatfaq_retrieval import RetrieverAnswerer
from scrapy.utils.project import get_project_settings
from django.apps import apps
from back.config.celery import app
from back.utils import is_celery_worker
from django.forms.models import model_to_dict
from scrapy.crawler import CrawlerRunner

logger = getLogger(__name__)


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
                repo_id=rag_conf.llm_config.repo_id,
                context_col="content",
                embedding_col="content",
                ggml_model_filename=rag_conf.llm_config.ggml_model_filename,
                use_cpu=False,
                model_config=rag_conf.llm_config.model_config,
                auth_token=rag_conf.llm_config.auth_token,
                load_in_8bit=rag_conf.llm_config.load_in_8bit,
                trust_remote_code_tokenizer=rag_conf.llm_config.trust_remote_code_tokenizer,
                trust_remote_code_model=rag_conf.llm_config.trust_remote_code_model,
                revision=rag_conf.llm_config.revision,
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
def initiate_crawl(knowledge_base_id, url):
    from back.apps.language_model.scraping.scraping.spiders.generic import GenericSpider  # CI
    runner = CrawlerRunner(get_project_settings())
    d = runner.crawl(GenericSpider, start_urls=url, knowledge_base_id=knowledge_base_id)
    d.addBoth(lambda _: reactor.stop())
    reactor.run()

