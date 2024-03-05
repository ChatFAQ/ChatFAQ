from typing import List, Callable
import re
import os

import nltk
from transformers import AutoTokenizer

class WordSplitter:
    """
    Splits a text into chunks of num_words words with an overlap of chunk_overlap words.
    """
    def __init__(self, chunk_size: int = 200, chunk_overlap: int = 20):
        """
        Parameters
        ----------
        chunk_size : int
            The number of words per chunk.
        overlap : int
            The number of words that overlap between two chunks.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
    def __call__(self, text: str) -> List[str]:
        """
        Splits a text into chunks of chunk_size words with an overlap of chunk_overlap words.
        Parameters
        ----------
        text : str
            The text to split.
        Returns
        -------
        List[str]
            A list of chunks.
        """
        words = text.split()
        if len(words) <= self.chunk_size:
            return [text]  # Do not split if text has fewer words than chunk_size
        chunks = []
        start = 0
        while start < len(words):
            end = start + self.chunk_size
            chunk = " ".join(words[start:end])
            # check if this chunk is a subset of the previous chunk
            if chunks and chunk in chunks[-1]:
                start += self.chunk_size - self.chunk_overlap
                continue
            chunks.append(chunk)
            start = end - self.chunk_overlap  # Move the start index for the next chunk
        return chunks
    

class CharacterSplitter:
    """
    Splits a text into chunks of num_chars characters with an overlap of overlap characters.
    """
    def __init__(self, num_chars: int, overlap: int):
        """
        Parameters
        ----------
        num_chars : int
            The number of characters per chunk.
        overlap : int
            The number of characters that overlap between two chunks.
        """
        self.num_chars = num_chars
        self.overlap = overlap
        
    def __call__(self, text: str) -> List[str]:
        """
        Splits a text into chunks of num_chars characters with an overlap of overlap characters.
        Parameters
        ----------
        text : str
            The text to split.
        Returns
        -------
        List[str]
            A list of chunks.
        """
        if len(text) <= self.num_chars:
            return [text]  # Do not split if text has fewer characters than num_chars
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.num_chars
            # If we're in the middle of a word, find the next space to end the chunk
            while end < len(text) and text[end] not in [' ', '\n', '\t']:
                end += 1
            chunk = text[start:end]
            # Check if this chunk is a subset of the previous chunk
            if chunks and chunk in chunks[-1]:
                # Adjust start to skip characters equal to specified overlap
                for _ in range(self.overlap):
                    while start < len(text) and text[start] != ' ':
                        start += 1
                    start += 1
                continue
            chunks.append(chunk)
            # Move the start index for the next chunk, ensuring the overlap starts from the beginning of a word
            overlap_chars = 0
            temp_start = end
            while (overlap_chars < self.overlap and temp_start > 0) and temp_start < len(text):
                temp_start -= 1
                if temp_start < 0:  # Avoid going out of bounds
                    break
                if text[temp_start] in [' ', '\n', '\t']:
                    break

            start = temp_start if overlap_chars == self.overlap else end
        return chunks
    

class TokenSplitter:
    """
    Splits a text into chunks of n xºtokens with an overlap of overlap tokens.
    Inspired by https://github.com/jerryjliu/llama_index/blob/main/llama_index/text_splitter/token_splitter.py
    """
    def __init__(self, tokenizer_name="intfloat/e5-small-v2", chunk_size: int = 128, chunk_overlap: int = 16, separators: List[str] = ["\n", "\t", " "]):
        """
        Parameters
        ----------
        tokenizer_name : str
            The name of the tokenizer to use.
        chunk_size : int
            The number of tokens per chunk.
        chunk_overlap : int
            The number of tokens that overlap between two chunks.
        separators : List[str]
            A list of separators to split on.
        """
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name) 
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators
        self.sep_pattern = '(?={})'.format('|'.join(map(re.escape, separators))) # regex pattern to split on separators

    def __call__(self, text):
        """
        Splits a text into chunks of n xºtokens with an overlap of overlap tokens.
        Parameters
        ----------
        text : str
            The text to split.
        Returns
        -------
        List[str]
            A list of chunks.
        """
        # First, we split using our regular expression pattern
        temp_split = re.split(self.sep_pattern, text)

        # Then, we group consecutive separators with the next word
        split_text = []
        buffer = ""
        for item in temp_split:
            if item in self.separators:
                buffer += item
            else:
                split_text.append(buffer + item)
                buffer = ""
        
        chunks = []
        current_chunk = []
        current_length = 0
        for split in split_text:
            n_tokens = len(self.tokenizer.tokenize(split))

            if current_length + n_tokens > self.chunk_size:
                chunks.append("".join(current_chunk).strip())
                # start a new chunk with overlap
                # keep popping off the first element until we have enough space
                while current_length > self.chunk_overlap or current_length + n_tokens > self.chunk_size:
                    # pop off the first element
                    first_chunk = current_chunk.pop(0)
                    current_length -= len(self.tokenizer.tokenize(first_chunk))
                    
            current_chunk.append(split)
            current_length += n_tokens

        if len(current_chunk) > 0:
            chunks.append("".join(current_chunk).strip())

        return chunks
    

class SentenceTokenSplitter:
    """
    Splits a text into chunks of sentences according to the number of tokens.
    """
    def __init__(self, tokenizer_name="intfloat/e5-small-v2", chunk_size: int = 128):
        """
        Parameters
        ----------
        tokenizer_name : str
            The name of the tokenizer to use.
        chunk_size : int
            The number of tokens per chunk.
        """
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name) 
        self.chunk_size = chunk_size

    def __call__(self, text):
        """
        Splits a text into chunks of sentences according to the number of tokens.
        Parameters
        ----------
        text : str
            The text to split.
        Returns
        -------
        List[str]
            A list of chunks.
        """

        # First, we split the text into sentences
        sentences = nltk.sent_tokenize(text)  
        
        chunks = []
        current_chunk = []
        current_length = 0
        for sentence in sentences:
            n_tokens = len(self.tokenizer.tokenize(sentence))

            if current_length + n_tokens > self.chunk_size and len(current_chunk) > 0: # if the current sentence does not fit in the current chunk, start a new chunk
                chunks.append(" ".join(current_chunk).strip())
                current_chunk = []
                current_length = 0
                    
            current_chunk.append(sentence)
            current_length += n_tokens

        if len(current_chunk) > 0: # add the last chunk
            chunks.append(" ".join(current_chunk).strip())

        return chunks
    

class SmartSplitter:
    """
    Splits the text into information meaningful chunks using the GPT-4 model.
    This can reach API rate limits very quickly.
    """
    def __init__(self, model_name='gpt-4-0125-preview'):
        """
        Parameters
        ----------
        model_name : str
            The name of the model to use. The recommended model is 'gpt-4', do not guarantee that other models will work.
        """
        from openai import OpenAI
        
        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

        self.model_name = model_name
        
        self.system_prompt = """You are designed to function as an informative assistant. 
- When provided with user input, your primary task is to discern and segregate the text into distinct segments based on their inherent intents. 
- It's essential that each of these segments retains enough context to be useful for future information retrieval tasks. 
- Avoid creating overly short chunks, as they may lack necessary context. 
- If the user input is succinct and doesn't warrant segmentation, there's no obligation to segment it. 
- To ensure easy parsing during subsequent processing, separate each of these segmented chunks with the delimiter '###'."""

    def __call__(self, text):
        """
        Splits the text into information meaningful chunks using the GPT-4 model.
        Parameters
        ----------
        text : str
            The text to split.
        Returns
        -------
        List[str]
            A list of chunks.
        """
        

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": text},
        ]

        # Splitting the text into chunks
        response = self.client.chat.completions.create(model=self.model_name,
        messages=messages,
        temperature=0.2,
        max_tokens=1024,
        top_p=0.0,
        presence_penalty=0.0)

        messages.append({"role": "assistant", "content": response.choices[0]["message"]["content"]})
        chunks = response.choices[0]["message"]["content"].split("###")

        # Analyzing each chunk
        for ndx, chunk in enumerate(chunks):
            print(f"Chunk {ndx} of {len(chunks)}", flush=True)
            user_content = f"Analyze this chunk:\n{chunk}" if ndx else f"Reflect upon the answer you produced based on the previous system instruction. Provide feedback on the performance, mentioning any areas of improvement or points of adherence. It's very important that each chunk can be understood on its own. Let's go chunk by chunk.\nAnalyze this chunk:\n{chunk}"
            messages.append({"role": "user", "content": user_content})

            response = self.client.chat.completions.create(model=self.model_name,
            messages=messages,
            temperature=1,
            max_tokens=1024,
            top_p=0.0,
            presence_penalty=0.0)
            messages.append({"role": "assistant", "content": response.choices[0]["message"]["content"]})

        # Refining chunks based on feedback
        messages.append(
            {"role": "user", "content": "Refine your chunks given the feedback that you provided. Remember that a segmentation is not always needed and just write the chunks."}
        )

        response = self.client.chat.completions.create(model=self.model_name,
        messages=messages,
        temperature=0.2,
        max_tokens=1024,
        top_p=0.0,
        presence_penalty=0.0)

        final_chunks = response.choices[0]["message"]["content"].split("###")

        return final_chunks
    

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
        return SentenceTokenSplitter(chunk_size=chunk_size)
    elif splitter == 'words':
        return WordSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    elif splitter == 'tokens':
        return TokenSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    elif splitter == 'smart':
        return SmartSplitter()
    else:
        raise ValueError(f"Unknown splitter: {splitter}, must be one of: sentences, words, tokens, smart")