import uuid
from logging import getLogger

import requests
from asgiref.sync import async_to_sync
from bs4 import BeautifulSoup
from celery import Task
from channels.layers import get_channel_layer
from chatfaq_retrieval import RetrieverAnswerer

from back.apps.language_model.models import Model
from back.config.celery import app
from back.utils import is_celery_worker

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
                m.dataset.original_file.file,
                m.base_model,
                "answer",
                "intent",
                use_cpu=True,
            )
            logger.info("...model loaded.")
        return cache

    @staticmethod
    def postprocess_context(context):
        for c in context:
            c["role"] = None
            if c.get("url"):
                soup = BeautifulSoup(requests.get(c["url"]).text)
                c["url_title"] = soup.title.get_text()
                icon_link = soup.find("link", rel="shortcut icon")
                icon_link = icon_link if icon_link else soup.find("link", rel="icon")
                c["url_icon"] = icon_link["href"]


@app.task(bind=True, base=LLMCacheOnWorkerTask)
def llm_query_task(self, chanel_name, model_id, input_text, bot_channel_name):
    channel_layer = get_channel_layer()

    lm_msg_id = str(uuid.uuid4())
    context = []
    msg_template = {
        "bot_channel_name": bot_channel_name,
        "lm_msg_id": lm_msg_id,
        "context": context,
        "final": False,
        "res": "",
    }
    for res in self.CACHED_MODELS[str(model_id)].query(input_text, streaming=True):
        if not res["res"]:
            continue
        if not context:
            [context.append(c) for c in res["context"]]
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
    self.postprocess_context(msg_template["context"])
    async_to_sync(channel_layer.send)(
        chanel_name,
        {
            "type": "send_llm_response",
            "message": msg_template,
        },
    )
