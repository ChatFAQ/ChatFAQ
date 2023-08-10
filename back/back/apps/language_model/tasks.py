import uuid
from io import StringIO
from logging import getLogger
from twisted.internet import reactor
from asgiref.sync import async_to_sync
from celery import Task
from channels.layers import get_channel_layer
from chatfaq_retrieval import RetrieverAnswerer
from scrapy.utils.project import get_project_settings
from back.apps.language_model.models import Model
from back.apps.language_model.models import PromptStructure
from back.apps.language_model.models import GenerationConfig
from back.config.celery import app
from back.utils import is_celery_worker
from django.forms.models import model_to_dict
from scrapy.crawler import CrawlerRunner
from back.apps.language_model.scraping.scraping.spiders.generic import GenericSpider

logger = getLogger(__name__)


class LLMCacheOnWorkerTask(Task):
    def __init__(self):
        self.CACHED_MODELS = {}
        if is_celery_worker():
            self.CACHED_MODELS = self.preload_models()

    @staticmethod
    def preload_models():
        logger.info("Preloading models...")
        cache = {}
        for m in Model.objects.all():
            logger.info(f"Loading models {m.name}")
            cache[str(m.pk)] = RetrieverAnswerer(
                base_data=StringIO(m.dataset.to_csv()),
                repo_id=m.repo_id,
                context_col="answer",
                embedding_col="intent",
                ggml_model_filename=m.ggml_model_filename,
                use_cpu=False,
                model_config=m.model_config,
                auth_token=m.auth_token,
                load_in_8bit=m.load_in_8bit,
                trust_remote_code_tokenizer=m.trust_remote_code_tokenizer,
                trust_remote_code_model=m.trust_remote_code_model,
                revision=m.revision,
            )
            logger.info("...model loaded.")
        return cache


@app.task(bind=True, ignore_result=True, base=LLMCacheOnWorkerTask)
def recache_models(self):
    self.CACHED_MODELS = self.preload_models()


@app.task(bind=True, base=LLMCacheOnWorkerTask)
def llm_query_task(self, chanel_name, model_id, input_text, conversation_id, bot_channel_name):
    channel_layer = get_channel_layer()

    msg_template = {
        "bot_channel_name": bot_channel_name,
        "lm_msg_id": str(uuid.uuid4()),
        "context": None,
        "final": False,
        "res": "",
    }
    model = self.CACHED_MODELS[str(model_id)]
    # get the prompt structure corresponding to the model using the foreign key
    prompt_structure = PromptStructure.objects.filter(model=model_id).first()
    generation_config = GenerationConfig.objects.filter(model=model_id).first()
    prompt_structure = model_to_dict(prompt_structure)
    generation_config = model_to_dict(generation_config)

    # remove the id and model fields from the prompt structure and generation config
    prompt_structure.pop("id")
    prompt_structure.pop("model")
    generation_config.pop("id")
    generation_config.pop("model")

    # remove the tags and end tokens from the stop words
    stop_words = [prompt_structure["user_tag"], prompt_structure["assistant_tag"], prompt_structure["user_end"], prompt_structure["assistant_end"]]

    # remove empty stop words
    stop_words = [word for word in stop_words if word]

    # # Gatherings all the previous messages from the conversation
    # prev_messages = Conversation.objects.get(pk=conversation_id).get_mml_chain()

    streaming = True
    if streaming:
        for res in model.stream(
            input_text,
            prompt_structure_dict=prompt_structure,
            generation_config_dict=generation_config,
            stop_words=stop_words,
            lang=Model.objects.get(pk=model_id).dataset.lang,
        ):
            if not res["res"]:
                continue
            if not msg_template["context"]:
                msg_template["context"] = res["context"]
            msg_template["res"] = res["res"]

            async_to_sync(channel_layer.send)(
                chanel_name,
                {
                    "type": "send_llm_response",
                    "message": msg_template,
                },
            )
    else:
        res = model.generate(
            input_text,
            prompt_structure_dict=prompt_structure,
            generation_config_dict=generation_config,
            stop_words=stop_words,
            lang=Model.objects.get(pk=model_id).dataset.lang,
        )

        if not msg_template["context"]:
            msg_template["context"] = res["context"]
        msg_template["res"] = res["res"]

        async_to_sync(channel_layer.send)(
            chanel_name,
            {
                "type": "send_llm_response",
                "message": msg_template,
            },
        )

    msg_template["res"] = ""
    msg_template["final"] = True

    async_to_sync(channel_layer.send)(
        chanel_name,
        {
            "type": "send_llm_response",
            "message": msg_template,
        },
    )


@app.task()
def initiate_crawl(dataset_id, url):
    runner = CrawlerRunner(get_project_settings())
    d = runner.crawl(GenericSpider, start_urls=url, dataset_id=dataset_id)
    d.addBoth(lambda _: reactor.stop())
    reactor.run()

