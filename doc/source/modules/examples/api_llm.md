# Use ChatFAQ with an API LLM

## Overview

### Benefits of using ChatFAQ with an API LLM

- **Pay as you go:** API-based LLMs often utilize a pay-per-token model. This means you only incur costs when ChatFAQ actively leverages the LLM for responses,  offering a flexible and potentially cost-effective solution for smaller or fluctuating usage patterns.

- **No need to deploy another component for running the LLM:** Using an API-based LLM eliminates the overhead of deploying, managing, and scaling the LLM infrastructure yourself.  This simplifies your setup, reduces maintenance, and allows you to focus on building and improving your chatbot.

- **In most cases cheaper, unless you have a high volume of requests:** API-based LLMs are often a cost-effective solution for low to moderate usage volumes. As your chatbot grows and handles a very high volume of requests, it might become advantageous to explore deploying your own LLM for potential cost savings at scale.

### Supported LLM providers

Currently, we support the following LLM providers:

- [OpenAI GPT models](https://platform.openai.com/docs/api-reference)
- [Mistral models](https://docs.mistral.ai/)
- [Anthropic Claude models](https://docs.anthropic.com/claude/reference/getting-started-with-the-api)

## Prerequisites

- ChatFAQ installation and setup.
- API key and credentials for your chosen LLM provider.
- A knowledge base with the data sources that you want to use, you can check the [PDF data source](pdf_data_source.md) example to see how to create a knowledge base with PDFs as the data source, or the [CSV data source](csv_data_source.md) example to see how to create a knowledge base with CSVs as the data source.

## Step-by-step guide

For this example let's use GPT-4 Turbo from OpenAI and this [ColBERT model](colbert-ir/colbertv2.0) for the retrieval part. Make sure that you have the API key for OpenAI and that you have added it to the `back/.env` file as `OPENAI_API_KEY=<your_api_key>`.

To create a new RAG we need to have 5 components first:

- A retriever.
- The system prompt to tell the LLM how to behave.
- A generation configuration for the LLM.
- The LLM itself.
- A knowledge base with knowledge items, in this case, we will use a knowledge base with the sample CSV provided in the [CSV data source](csv_data_source.md) example.
  
> We provide extensive documentation of each of these components in the [AI Configuration documentation](../configuration/index.md).

1. Let's start by creating the retriever. Go to the admin and click on the AI Configuration section. Then click on the "Retrievers" tab and add a new retriever. For the retriever type select `ColBERT` and for the model name write `colbert-ir/colbertv2.0`. Put `colbert_english` as the name and click on "Save".
2. Go to the generation configurations tab and add a new generation configuration. For the generation configuration select the default values, for the name put 'default_gen_config' and click on "Save".
3. Go to the LLM tab and add a new LLM. For the LLM type select `openai` and for the model name write `gpt-4-0125-preview`. Put `gpt-4` as the name and click on "Save".
4. Go to the prompt tab and add a new prompt. As the system prefix you can copy and paste the system prompt below. Put `chatfaq_prompt` as the name and click on "Save". The system prompt is:

```plaintext
- ChatFAQ is a Open-source RAG framework for deploying LLMs in enterprises
- Your task is to provide an answer based on the information extracts only. Never provide an answer if you don't have the necessary information in the relevant extracts.
- If the question is not about ChatFAQ, politely inform them that you are tuned to only answer questions about ChatFAQ.
```

5. Finally, go to the RAG tab and add a new RAG. For the name put `default` and for the retriever, generation configuration, LLM and prompt select the ones that we created before. Click on "Save".
6. Now, so the RAG can work, we need to index the knowledge base. In the RAG tab you can see an `index` button, when you click on it a new task will be created and the knowledge base will be indexed. After the task is finished you can start using the RAG, wait a few seconds so the RAG is loaded and then you can start asking questions where you deployed your widget.
