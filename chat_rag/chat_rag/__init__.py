from logging import getLogger
from typing import List, Dict

from chat_rag.llms import RAGLLM
from chat_rag.inf_retrieval.reference_checker import ReferenceChecker, clean_relevant_references

logger = getLogger(__name__)


class RAG:
    """
    Class for generating responses using the Retrieval-Augmented Generation (RAG) pattern.
    """
    def __init__(
        self,
        retriever,
        llm_model: RAGLLM,
        reference_checker: bool = True,
        lang: str = "en",
    ):
        """
        Args:
            retriever: A retriever object that has a `retrieve` method.
            llm_model: A RAGLLM object that has a `generate` method.
            reference_checker: A boolean indicating whether to use a reference checker, to check if the user messages need to retrieve new contexts.
        """
        
        self.retriever = retriever
        self.model = llm_model
        self.reference_checker = ReferenceChecker(lang, device=retriever.embedding_model.device) if reference_checker else None
        self.lang = lang


    def retrieve(
        self,
        message: str,
        prev_contents: List[str],
        prompt_structure_dict: dict,
    ):
        """
        Retrieve new contexts if needed.
        """
        if self.reference_checker is not None and self.reference_checker.check_references(message):
            logger.info("Retrieving new contexts")
            contexts = self.retriever.retrieve([message], top_k=prompt_structure_dict["n_contexts_to_use"])[0] # retrieve contexts
            contexts = clean_relevant_references(contexts) # clean contexts
            contents = [context["content"] for context in contexts] # get unique contexts
            returned_contexts = [contexts[:prompt_structure_dict["n_contexts_to_use"]]] # structure for references
            contents = list(set(contents + prev_contents))

            return contents, returned_contexts
        else:
            logger.info("Not retrieving new contexts")
            return prev_contents, []

    def stream(
        self,
        messages: List[Dict[str, str]],
        prev_contents: List[str],
        prompt_structure_dict: dict,
        generation_config_dict: dict,
        stop_words: List[str] = None,
    ):

        # Retrieve
        contents, returned_contexts = self.retrieve(messages[-1]['content'], prev_contents, prompt_structure_dict)

        # Generate
        for new_text in self.model.stream(
            messages,
            contents,
            prompt_structure_dict=prompt_structure_dict,
            generation_config_dict=generation_config_dict,
            lang=self.lang,
            stop_words=stop_words,
        ):
            yield {
                "res": new_text,
                "context": returned_contexts,
            }

    def generate(
        self,
        messages: List[Dict[str, str]],
        prev_contents: List[str],
        prompt_structure_dict: dict,
        generation_config_dict: dict,
        stop_words: List[str] = None,
    ):
        
        # Retrieve
        contents, returned_contexts = self.retrieve(messages[-1]['content'], prev_contents, prompt_structure_dict)       

        output_text = self.model.generate(
            messages,
            contents,
            prompt_structure_dict=prompt_structure_dict,
            generation_config_dict=generation_config_dict,
            lang=self.lang,
            stop_words=stop_words,
        )

        return {
            "res": output_text,
            "context": returned_contexts,
        }
