import time

from celery import Task
from logging import getLogger
from asgiref.sync import async_to_sync
from chatfaq_retrieval import RetrieverAnswerer
from channels.layers import get_channel_layer
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
                use_cpu=True
            )
            logger.info("...model loaded.")
        return cache


@app.task(bind=True, base=LLMCacheOnWorkerTask)
def llm_query_task(self, chanel_name, model_id, input_text, bot_channel_name):
    channel_layer = get_channel_layer()
    res = self.CACHED_MODELS[str(model_id)].query(input_text)
    for c in res["context"]:
        c["role"] = None
    res["bot_channel_name"] = bot_channel_name

    # Faking streaming ------>>
    full_sentence = res["res"]
    full_sentence = "this is a test blah blah"
    def split_by_n(seq, n):
        while seq:
            yield seq[:n]
            seq = seq[n:]
    splitted = list(split_by_n(full_sentence, 5))
    for index, word in enumerate(splitted):
        res["res"] = word
        res["final"] = False
        if index == len(splitted) - 1:
            res["final"] = True
        async_to_sync(channel_layer.send)(chanel_name, {
            'type': 'send_llm_response',
            'message': res
        })
        time.sleep(0.5)
