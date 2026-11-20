# ChatFAQ NLP Engine

This is the NLP Engine for ChatFAQ. It is divided in two modules:

1. Information Retrieval: This module is responsible for retrieving the most relevant answer to a given question.
2. Chatbot: This module is responsible for generating a response to the given question based on the retrieved answer and chat with the user.

# Information Retrieval

The `Retriever` is the main class for the information retrieval system. It takes as input a question (query) and a context and returns the most relevant sentences from the context to the query. This is done using embeddings and the dot product to compute the similarity between the query and the context sentences.


# Chatbot


## Chatbot

The `RetrieverAnswerer` is the main class for the chatbot. It takes as input a question (query) and a context and returns a response to the query. This is done by first retrieving the most relevant sentences from the context to the query and then generating a response based on the retrieved sentences.

## Python 3.14 and document parsing

`chat-rag 0.2.15` supports Python 3.14 for its chatbot, LLM, retrieval, and
embedding functionality. PDF and HTML parsing through
`chat_rag.data.parsers` is not currently available on Python 3.14 because its
upstream dependencies, `unstructured` and `unstructured-inference`, require
Python `<3.14`.

This is not a regression introduced by `0.2.15`. The previous package
configuration constrained `unstructured` to Python `>=3.10,<3.12`, while
`chat-rag 0.2.14` itself targeted Python 3.13. Consequently, the parser was
already unavailable on Python 3.12 and 3.13. The incompatible dependencies
have been removed from the `full` extra and `ml` group so those installation
targets remain resolvable on Python 3.14.

Calling `parse_pdf()` or `parse_html()` without a compatible parser stack
raises `ParsingUnavailableError` with this compatibility context instead of an
unexplained `ModuleNotFoundError`. Document parsing must run in a separate
environment supported by `unstructured` until upstream adds Python 3.14
support or the parser is replaced.


# Publish package

### PYPI test

add repository to poetry config

    poetry config repositories.test-pypi https://test.pypi.org/legacy/

get token from https://test.pypi.org/manage/account/token/

store token using

    poetry config pypi-token.test-pypi pypi-YYYYYYYY

### PYPI production

get token from https://pypi.org/manage/account/token/

store token using

    poetry config pypi-token.chat-rag pypi-XXXXXXXX

Each time you need to publish

Bump version

    poetry version prerelease

or

    poetry version patch

Then build

    poetry build

### Poetry Publish

To TestPyPi

    poetry publish -r test-pypi

To PyPi

    poetry publish
