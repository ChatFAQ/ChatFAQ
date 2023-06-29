import os

from ctransformers import AutoModelForCausalLM, AutoConfig


class GGMLModel:

    def __init__(self, model_id: str, model_filename: str, model_config: str, model_kwargs: dict = None):
        """
        Initializes the ggml model. Optimized for CPU inference
        Parameters
        ----------
        model_id : str
            The huggingface model id.
         model_filename: str
            The filename of the model to load
        model_kwargs : dict
            Keyword arguments for the model.
        """

        config = AutoConfig.from_pretrained(model_config)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id, 
            config=config,
            **model_kwargs,
        )


    def generate(self, prompt, seed=42, streaming=False, generation_kwargs: dict = None) -> str:
        """
        Generate text from a prompt using the model.
        Parameters
        ----------
        prompt : str
            The prompt to generate text from.
        seed : int
            The seed to use for generation.
        streaming : bool
            Whether to use streaming generation.
        generation_kwargs : dict
            Keyword arguments for the generation.
        Returns
        -------
        str
            The generated text.
        """

        assert streaming == generation_kwargs['stream'], "Streaming must be set in generation_kwargs"

        # if threads not in generation_kwargs, then set threads to half of the available cores
        if 'threads' not in generation_kwargs:
            generation_kwargs['threads'] = os.cpu_count() // 2


        if streaming:
            streamer = self.model(prompt, **generation_kwargs) # returns a generator
            for word in streamer:
                yield word
        else:
            text = self.model(prompt, **generation_kwargs)
            return text
            


