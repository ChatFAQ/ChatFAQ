from logging import getLogger
from typing import List, Dict
from chat_rag.llms import RAGLLM

logger = getLogger(__name__)

class AsyncRAG:
    """ Class for generating responses using the Retrieval-Augmented Generation (RAG) pattern in an asynchronous manner. """
    def __init__(
        self,
        retriever,
        llm_model: RAGLLM,
        lang: str = "en",
    ):
        """
        Parameters
        ----------
        retriever :
            Retriever object for retrieving contexts.
        llm_model : RAGLLM
            Language model for generating responses.
        lang : str, optional
            Language of the language model, by default "en"
        """

        self.retriever = retriever
        self.model = llm_model
        self.lang = lang

    async def retrieve(self, message: str, prev_contents: List[str], prompt_structure_dict: dict):
        """
        Retrieve new contexts if needed.

        Parameters
        ----------
        message : str
            User message.
        prev_contents : List[str]
            List of previous contexts.
        prompt_structure_dict : dict
            Dictionary containing the structure of the prompt.

        Returns
        -------
        Tuple[List[str], List[Dict[str, str]]]
            List of all conversation contexts and list of the retrieved contexts for the current user message.
        """
        logger.info("Retrieving new contexts")
        contexts = await self.retriever.retrieve(
            message,
            top_k=prompt_structure_dict["n_contexts_to_use"]
        )

        if not contexts:
            return [], []

        contents = [context["content"] for context in contexts]
        returned_contexts = [contexts[:prompt_structure_dict["n_contexts_to_use"]]]  # structure for references

        # Use a list comprehension to preserve order and not adding duplicates
        seen = set()
        contents = [x for x in prev_contents + contents if not (x in seen or seen.add(x))]
        return contents, returned_contexts

    async def stream(self, messages: List[Dict[str, str]], prev_contents: List[str], prompt_structure_dict: dict, generation_config_dict: dict, stop_words: List[str] = None):
        # Retrieve
        contents, returned_contexts = await self.retrieve(messages[-1]['content'], prev_contents, prompt_structure_dict)

        # Generate
        async for new_text in self.model.stream(
            messages, contents, prompt_structure_dict=prompt_structure_dict,
            generation_config_dict=generation_config_dict, lang=self.lang, stop_words=stop_words
        ):
            yield {"res": new_text, "context": returned_contexts}

    async def generate(self, messages: List[Dict[str, str]], prev_contents: List[str], prompt_structure_dict: dict, generation_config_dict: dict, stop_words: List[str] = None):
        # Retrieve
        contents, returned_contexts = await self.retrieve(messages[-1]['content'], prev_contents, prompt_structure_dict)

        output_text = await self.model.generate(
            messages, contents, prompt_structure_dict=prompt_structure_dict,
            generation_config_dict=generation_config_dict, lang=self.lang, stop_words=stop_words
        )
        return {"res": output_text, "context": returned_contexts}