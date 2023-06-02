# ChatFAQ NLP Engine

This is the NLP Engine for ChatFAQ. It is divided in two modules:

1. Information Retrieval: This module is responsible for retrieving the most relevant answer to a given question.
2. Chatbot: This module is responsible for generating a response to the given question based on the retrieved answer and chat with the user.

# Information Retrieval

The `Retriever` is the main class for the information retrieval system. It takes as input a question (query) and a context and returns the most relevant sentences from the context to the query. This is done using embeddings and the dot product to compute the similarity between the query and the context sentences.


# Chatbot

## Prompt Generator

The `PromptGenerator` is the main class for generating the prompts.


## Chatbot

The `RetrieverAnswerer` is the main class for the chatbot. It takes as input a question (query) and a context and returns a response to the query. This is done by first retrieving the most relevant sentences from the context to the query and then generating a response based on the retrieved sentences.

