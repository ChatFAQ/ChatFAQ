import tempfile

# from ir_qa_dev import RetrieverAnswerer
from logging import getLogger
import requests

logger = getLogger(__name__)


class Layer:
    """
    Representation of all the future stack's layers. Implementing a new layer should inherit form this
    """

    _type = None

    def dict_repr(self, ctx) -> dict:
        """
        Used to represent the layer as a dictionary which will be sent through the WS to the ChatFAQ's back-end server
        It is cached since there are layers as such as the LMGeneratedText which are computationally expensive
        :return:
            dict
                A json compatible dict
        """
        raise NotImplementedError


class Text(Layer):
    """
    Simplest layer representing raw text
    """

    _type = "text"

    def __init__(self, payload):
        self.payload = payload

    def dict_repr(self, ctx):
        return [{"type": self._type, "payload": self.payload}]


"""
class LMGeneratedText(Layer):
"""\
"""
Layer representing text generated by a language model
"""
"""

    _type = "lm_generated_text"
    loaded_model = {}

    @classmethod
    def get_model(cls, model_id, ctx):

        if model_id not in cls.loaded_model:
            logger.info("Loafing model...")
            headers = {
                "Authorization": f"Token {ctx.token}"
            }
            # TODO use the Python client (refactor CLI to use it too)
            model_res = requests.get(f"{ctx.chatfaq_http}/back/api/language-model/models/{model_id}/", headers=headers).json()
            dataset_res = requests.get(f"{ctx.chatfaq_http}/back/api/language-model/datasets/{model_res['dataset']}/download_csv/")

            _file = dataset_res.content

            tmp_path = tempfile.NamedTemporaryFile().name + ".csv"
            # Open the file for writing.
            with open(tmp_path, 'wb') as f:
                f.write(_file)

                cls.loaded_model[model_id] = RetrieverAnswerer(
                    tmp_path,
                    model_res["base_model"],
                    "answer",
                    "intent",
                    use_cpu=True
                )
                logger.info("...model loaded.")
                pass
        return cls.loaded_model[model_id]

    def __init__(self, input_text, model_id):
        self.input_text = input_text
        self.model_id = model_id

    def dict_repr(self, ctx):
        model = self.get_model(self.model_id, ctx)
        return [{"type": self._type, "payload": {"model_response": model.query(self.input_text), "model": self.model_id}}]
"""
