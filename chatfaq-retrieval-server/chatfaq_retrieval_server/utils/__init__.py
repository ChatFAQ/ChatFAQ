from chatfaq_retrieval import RetrieverAnswerer
from django.conf import settings
import tempfile
import requests
from logging import getLogger

logger = getLogger(__name__)


def get_model(model_id):
    if model_id not in settings.CACHED_MODELS:
        logger.info("Loafing model...")
        headers = {
            "Authorization": f"Token {settings.CHATFAQ_TOKEN}",
        }
        # TODO use the Python client (refactor CLI to use it too)
        model_res = requests.get(f"{settings.CHATFAQ_HTTP}/back/api/language-model/models/{model_id}/", headers=headers).json()
        dataset_res = requests.get(f"{settings.CHATFAQ_HTTP}/back/api/language-model/datasets/{model_res['dataset']}/download_csv/")

        _file = dataset_res.content

        tmp_path = tempfile.NamedTemporaryFile().name + ".csv"
        # Open the file for writing.
        with open(tmp_path, 'wb') as f:
            f.write(_file)

            settings.CACHED_MODELS[model_id] = RetrieverAnswerer(
                tmp_path,
                model_res["base_model"],
                "answer",
                "intent",
                use_cpu=True
            )
            logger.info("...model loaded.")
            pass
    return settings.CACHED_MODELS[model_id]
