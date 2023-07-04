import uuid
from logging import getLogger

from asgiref.sync import async_to_sync
from celery import Task
from channels.layers import get_channel_layer
from chatfaq_retrieval import RetrieverAnswerer

from back.apps.language_model.models import Model
from back.apps.language_model.models import PromptStructure
from back.apps.language_model.models import GenerationConfig
from back.config.celery import app
from back.utils import is_celery_worker
from django.forms.models import model_to_dict

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
                base_data=m.dataset.original_file.file,
                repo_id=m.repo_id,
                context_col="answer",
                embedding_col="intent",
                ggml_model_filename=m.ggml_model_filename,
                use_cpu=True,
                model_config=m.model_config,
                huggingface_auth_token=m.huggingface_auth_token,
                load_in_8bit=m.load_in_8bit,
                trust_remote_code_tokenizer=m.trust_remote_code_tokenizer,
                trust_remote_code_model=m.trust_remote_code_model,
                revision=m.revision,
            )
            logger.info("...model loaded.")
        return cache


@app.task(bind=True, base=LLMCacheOnWorkerTask)
def llm_query_task(self, chanel_name, model_id, input_text, bot_channel_name):
    channel_layer = get_channel_layer()

    lm_msg_id = str(uuid.uuid4())
    msg_template = {
        "bot_channel_name": bot_channel_name,
        "lm_msg_id": lm_msg_id,
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

    prompt_structure.pop("id")
    prompt_structure.pop("model")
    generation_config.pop("id")
    generation_config.pop("model")

    stop_words = [prompt_structure["user_tag"], prompt_structure["assistant_tag"]]

    for res in model.query(
        input_text,
        prompt_structure_dict=prompt_structure,
        generation_config_dict=generation_config,
        stop_words=stop_words,
        lang=Model.objects.get(pk=model_id).dataset.lang,
        streaming=True,
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

    msg_template["res"] = ""
    msg_template["final"] = True

    async_to_sync(channel_layer.send)(
        chanel_name,
        {
            "type": "send_llm_response",
            "message": msg_template,
        },
    )
