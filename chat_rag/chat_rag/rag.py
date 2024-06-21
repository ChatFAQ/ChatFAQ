from logging import getLogger
from typing import Dict, List

from chat_rag.llms import LLM

logger = getLogger(__name__)


CONTEXT_PREFIX = {
    "en": "Information:",
    "fr": "Informations:",
    "es": "Información:",
}

NO_CONTEXT_SUFFIX = {
    "en": "No information provided.",
    "fr": "Aucune information n'a été fournie.",
    "es": "No se proporciona información.",
}


class RAG:
    """
    Class for generating responses using the Retrieval-Augmented Generation (RAG) pattern.
    """

    def __init__(
        self,
        retriever,
        llm: LLM,
        lang: str = "en",
    ):
        """
        Parameters
        ----------
        retriever :
            Retriever object for retrieving contexts.
        llm : RAGLLM
            Language model for generating responses.
        lang : str, optional
            Language of the language model, by default "en"
        """

        self.retriever = retriever
        self.llm = llm
        self.lang = lang

    def _get_unique_contexts(self, prev_contents, n_contexts_to_use, contexts):
        """
        Get unique contexts from the retrieved contexts.
        """
        if len(contexts) == 0:
            return [], []
        contents = [context["content"] for context in contexts]  # get unique contexts
        returned_contexts = [contexts[:n_contexts_to_use]]  # structure for references

        # Use a list comprehension to preserve order and not adding duplicates
        seen = set()
        contents = [
            x for x in prev_contents + contents if not (x in seen or seen.add(x))
        ]
        
        return contents,returned_contexts

    def retrieve(
        self,
        message: str,
        prev_contents: List[str],
        n_contexts_to_use: int = 3,
    ):
        """
        Retrieve new contexts if needed.
        Parameters
        ----------
        message : str
            User message.
        prev_contents : List[str]
            List of previous contexts.
        n_contexts_to_use : int, optional
            Number of contexts to retrieve, by default 3.
        Returns
        -------
        Tuple[List[str], List[Dict[str, str]]]
            List of all conversation contexts and list of the retrieved contexts for the current user message.
        """
        logger.info("Retrieving new contexts")
        contexts = self.retriever.retrieve([message], top_k=n_contexts_to_use)[0]

        return self._get_unique_contexts(prev_contents, n_contexts_to_use, contexts)

    async def aretrieve(
        self,
        message: str,
        prev_contents: List[str],
        n_contexts_to_use: int = 3,
    ):
        """
        Retrieve new contexts if needed.
        Parameters
        ----------
        message : str
            User message.
        prev_contents : List[str]
            List of previous contexts.
        n_contexts_to_use : int, optional
            Number of contexts to retrieve, by default 3.
        Returns
        -------
        Tuple[List[str], List[Dict[str, str]]]
            List of all conversation contexts and list of the retrieved contexts for the current user message.
        """
        logger.info("Retrieving new contexts")
        contexts = await self.retriever.retrieve([message], top_k=n_contexts_to_use)

        contexts = contexts[0]

        return self._get_unique_contexts(prev_contents, n_contexts_to_use, contexts)

    def augment_prompt(
        self,
        messages: List[Dict[str, str]],
        contexts: List[str],
        lang: str = "en",
    ) -> List[Dict[str, str]]:
        """
        Add the contexts to the system prompt to be used by the model, example:
        <<System Prompt>>
        <<Context Prefix>>
        - context 1
        - ...
        - contextN
        """

        system_prompt = messages.pop(0)["content"]
        if len(contexts) > 0:
            system_prompt = f"{system_prompt}\n{CONTEXT_PREFIX[lang]}\n"

            for ndx, context in enumerate(contexts):
                system_prompt += f"- {context}"

                if ndx < len(contexts) - 1:  # no newline on last context
                    system_prompt += "\n"

        else:
            system_prompt + f"\n{CONTEXT_PREFIX[lang]}\n{NO_CONTEXT_SUFFIX[lang]}"

        messages = [{"role": "system", "content": system_prompt}] + messages

        return messages

    def stream(
        self,
        messages: List[Dict[str, str]],
        prev_contents: List[str],
        temperature: float = 0.2,
        max_tokens: int = 1024,
        seed: int = None,
        n_contexts_to_use: int = 3,
    ):
        # Retrieve
        contents, returned_contexts = self.retrieve(
            messages[-1]["content"], prev_contents, n_contexts_to_use
        )

        # Augment
        messages = self.augment_prompt(messages, contents, self.lang)

        # Generate
        for new_text in self.llm.stream(
            messages,
            temperature,
            max_tokens,
            seed,
        ):
            yield {
                "res": new_text,
                "context": returned_contexts,
            }

    async def astream(
        self,
        messages: List[Dict[str, str]],
        prev_contents: List[str],
        temperature: float = 0.2,
        max_tokens: int = 1024,
        seed: int = None,
        n_contexts_to_use: int = 3,
    ):
        # Retrieve
        contents, returned_contexts = await self.aretrieve(
            messages[-1]["content"], prev_contents, n_contexts_to_use
        )

        # Augment
        messages = self.augment_prompt(messages, contents, self.lang)

        # Generate
        async for new_text in self.llm.astream(
            messages,
            temperature,
            max_tokens,
            seed,
        ):
            yield {
                "res": new_text,
                "context": returned_contexts,
            }

    def generate(
        self,
        messages: List[Dict[str, str]],
        prev_contents: List[str],
        temperature: float = 0.2,
        max_tokens: int = 1024,
        seed: int = None,
        n_contexts_to_use: int = 3,
    ):
        # Retrieve
        contents, returned_contexts = self.retrieve(
            messages[-1]["content"], prev_contents, n_contexts_to_use
        )

        # Augment
        messages = self.augment_prompt(messages, contents, self.lang)

        # Generate
        output_text = self.llm.generate(
            messages,
            temperature,
            max_tokens,
            seed,
        )

        return {
            "res": output_text,
            "context": returned_contexts,
        }
    
    async def agenerate(
        self,
        messages: List[Dict[str, str]],
        prev_contents: List[str],
        temperature: float = 0.2,
        max_tokens: int = 1024,
        seed: int = None,
        n_contexts_to_use: int = 3,
    ):
        # Retrieve
        contents, returned_contexts = await self.aretrieve(
            messages[-1]["content"], prev_contents, n_contexts_to_use
        )

        # Augment
        messages = self.augment_prompt(messages, contents, self.lang)

        # Generate
        output_text = await self.llm.agenerate(
            messages,
            temperature,
            max_tokens,
            seed,
        )

        return {
            "res": output_text,
            "context": returned_contexts,
        }
