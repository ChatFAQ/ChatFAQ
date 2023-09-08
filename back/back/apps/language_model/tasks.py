import uuid
from io import StringIO, BytesIO
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


class LLMCacheOnWorkerTask(Task):
    CACHED_MODELS = {}

    def __init__(self):
        if is_celery_worker() and not self.CACHED_MODELS:
            self.CACHED_MODELS = self.preload_models()

    @staticmethod
    def preload_models():
        print("Preloading models...")
        Model = apps.get_model('language_model', 'Model')
        cache = {}
        for m in Model.objects.all():
            print(f"Loading model: {m.name} with dataset: {m.dataset.name}")
            cache[str(m.pk)] = RetrieverAnswerer(
                base_data=StringIO(m.dataset.to_csv()),
                repo_id=m.repo_id,
                context_col="answer",
                embedding_col="answer",
                ggml_model_filename=m.ggml_model_filename,
                use_cpu=False,
                model_config=m.model_config,
                auth_token=m.auth_token,
                load_in_8bit=m.load_in_8bit,
                trust_remote_code_tokenizer=m.trust_remote_code_tokenizer,
                trust_remote_code_model=m.trust_remote_code_model,
                revision=m.revision,
            )
            print("...model loaded.")
        return cache


@app.task(bind=True, base=LLMCacheOnWorkerTask)
def llm_query_task(self, chanel_name, model_id, input_text, conversation_id, bot_channel_name, recache_models):
    if recache_models:
        self.CACHED_MODELS = self.preload_models()
        return

    Model = apps.get_model('language_model', 'Model')
    PromptStructure = apps.get_model('language_model', 'PromptStructure')
    GenerationConfig = apps.get_model('language_model', 'GenerationConfig')
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
    from back.apps.language_model.scraping.scraping.spiders.generic import GenericSpider  # CI
    runner = CrawlerRunner(get_project_settings())
    d = runner.crawl(GenericSpider, start_urls=url, dataset_id=dataset_id)
    d.addBoth(lambda _: reactor.stop())
    reactor.run()


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
    from chatfaq_retrieval.data.parsers import parse_pdf

    Datasets = apps.get_model('language_model', 'Dataset')
    pdf_file = Datasets.objects.get(pk=pdf_file_pk).original_pdf.read()
    strategy = Datasets.objects.get(pk=pdf_file_pk).strategy
    splitter = Datasets.objects.get(pk=pdf_file_pk).splitter
    chunk_size = Datasets.objects.get(pk=pdf_file_pk).chunk_size
    chunk_overlap = Datasets.objects.get(pk=pdf_file_pk).chunk_overlap

    pdf_file = BytesIO(pdf_file)

    splitter = get_splitter(splitter, chunk_size, chunk_overlap)

    k_items = parse_pdf(file=pdf_file, strategy=strategy, split_function=splitter)

    # serialize the KnowledgeItem objects
    k_items = [k_item.__dict__ for k_item in k_items]

    return k_items


def get_splitter(splitter, chunk_size, chunk_overlap):
    """
    Returns the splitter object corresponding to the splitter name.
    """

    # check if chunk_size and chunk_overlap are valid and that the chunk_overlap is smaller than the chunk_size
    if chunk_size < 1:
        raise ValueError(f"chunk_size must be >= 1, got {chunk_size}")
    if chunk_overlap < 0:
        raise ValueError(f"chunk_overlap must be >= 0, got {chunk_overlap}")
    if chunk_overlap >= chunk_size:
        raise ValueError(f"chunk_overlap must be smaller than chunk_size, got chunk_overlap={chunk_overlap} and chunk_size={chunk_size}")
    

    if splitter == 'sentences':
        from chatfaq_retrieval.data.splitters import SentenceTokenSplitter
        return SentenceTokenSplitter(chunk_size=chunk_size)
    elif splitter == 'words':
        from chatfaq_retrieval.data.splitters import WordSplitter
        return WordSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    elif splitter == 'tokens':
        from chatfaq_retrieval.data.splitters import TokenSplitter
        return TokenSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    elif splitter == 'smart':
        from chatfaq_retrieval.data.splitters import SmartSplitter
        return SmartSplitter()
    else:
        raise ValueError(f"Unknown splitter: {splitter}, must be one of: sentences, words, tokens, smart")

        