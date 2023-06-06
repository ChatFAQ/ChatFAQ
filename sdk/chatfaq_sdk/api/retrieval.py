import requests
from logging import getLogger
logger = getLogger(__name__)


class ChatfaqRetrievalAPI:
    def __init__(self, chatfaq_retrieval_http, token):
        self.token = token
        self.chatfaq_retrieval_http = chatfaq_retrieval_http

    def query(self, model_id, input_text):
        logger.info("Requesting LLM...")
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        model_res = requests.get(
            f"{self.chatfaq_retrieval_http}/back/api/retriever/?model_id={model_id}&query={input_text}",
            headers=headers
        ).json()
        return model_res
