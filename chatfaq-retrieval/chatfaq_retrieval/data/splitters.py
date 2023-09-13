from typing import List, Callable

class WordSplitter:
    """
    Splits a text into chunks of num_words words with an overlap of overlap words.
    """
    def __init__(self, num_words: int = 200, overlap: int = 20):
        """
        Parameters
        ----------
        num_words : int
            The number of words per chunk.
        overlap : int
            The number of words that overlap between two chunks.
        """
        self.num_words = num_words
        self.overlap = overlap
        
    def __call__(self, text: str) -> List[str]:
        """
        Splits a text into chunks of num_words words with an overlap of overlap words.
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
        if len(words) <= self.num_words:
            return []  # Do not split if text has fewer words than num_words
        chunks = []
        start = 0
        while start < len(words):
            end = start + self.num_words
            chunk = " ".join(words[start:end])
            # check if this chunk is a subset of the previous chunk
            if chunks and chunk in chunks[-1]:
                start += self.num_words - self.overlap
                continue
            chunks.append(chunk)
            start = end - self.overlap  # Move the start index for the next chunk
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
            return []  # Do not split if text has fewer characters than num_chars
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.num_chars
            # If we're in the middle of a word, find the next space to end the chunk
            while end < len(text) and text[end] != ' ':
                end += 1
            chunk = text[start:end]
            # Check if this chunk is a subset of the previous chunk
            if chunks and chunk in chunks[-1]:
                start += self.num_chars - self.overlap
                continue
            chunks.append(chunk)
            start = end - self.overlap  # Move the start index for the next chunk
        return chunks