# Use ChatFAQ with an open-source LLM

## Overview

### Benefits of using ChatFAQ with an open-source LLM

- **Privacy and Control:**  By deploying the LLM on your own infrastructure, you maintain full control over your data. This can be crucial for applications dealing with sensitive information where data privacy is a top priority.

- **Potential Cost Savings (Long-Term):** While there might be initial setup costs involved, deploying an open-source LLM can potentially offer cost savings in the long run, especially for high-volume usage scenarios. You avoid recurring fees associated with API-based LLMs.

- **Customization:** Open-source LLMs offer you the flexibility to fine-tune the model to your specific domain. This can lead to greater understanding and relevance in ChatFAQ's responses, especially for niche topics.

### Popular open-source LLMs

There are two ways to use an open-source LLM with ChatFAQ:

- Using HuggingFace's Transformers for local deployment and use (`local gpu` in LLM config).
- Using [vLLM](https://github.com/vllm-project/vllm) for cloud-based deployment or you can use it locally also if you want faster response times (`vllm` in LLM config).

So we support every model that is compatible with HuggingFace's Transformers or vLLM.

As a recommendation, we suggest using the biggest LLM that you can afford to use, as bigger models tend to perform better in chatbot scenarios. For specific recommendations, we suggest any of the following models:

- The [Qwen 1.5 series](https://huggingface.co/collections/Qwen/qwen15-65c0a2f577b1ecb76d786524) from Alibaba Cloud.
- The [Zephyr series](https://huggingface.co/HuggingFaceH4) by HuggingFaceH4.
- The [Open Hermes series](https://huggingface.co/collections/teknium/open-hermes-652ff011fcb6dd376c337c39) by Teknium.

This list is not exhaustive and could be outdated, so we recommend that you check and test the latest models that fit your needs. The only requirement is that the model accepts a system prompt, so we can control its behavior.

## Prerequisites

- ChatFAQ installation and setup.
- API key and credentials for your chosen LLM provider.
- A knowledge base with the data sources that you want to use, you can check the [PDF data source](pdf_data_source.md) example to see how to create a knowledge base with PDFs as the data source, or the [CSV data source](csv_data_source.md) example to see how to create a knowledge base with CSVs as the data source.
- A GPU with at least **16GB** of VRAM.

## Step-by-step guide

For this example we are going to use a quantized version of Zephyr, [TheBloke/zephyr-7B-beta-AWQ](https://huggingface.co/TheBloke/zephyr-7B-beta-AWQ), with vLLM.

To create a new RAG we need to have 5 components first:

- A retriever.
- The system prompt to tell the LLM how to behave.
- A generation configuration for the LLM.
- The LLM itself.
- A knowledge base with knowledge items, in this case, we will use a knowledge base with the sample CSV provided in the [CSV data source](csv_data_source.md) example.
  
> We provide extensive documentation of each of these components in the [AI Configuration documentation](../configuration/index.md).

Before we start, we need to pull the docker image for vLLM:

```bash
docker pull vllm/vllm-openai:v0.3.3
```

Then, run the vLLM server with the following command:

```bash
docker run --runtime nvidia --gpus all \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    -p 5000:5000 \
    --ipc=host \
    vllm/vllm-openai:v0.3.3 --model TheBloke/zephyr-7B-beta-AWQ --port 5000 --quantization awq --gpu-memory-utilization 0.75 --max-model-len 4096
```

After running the command, the vLLM server will be running on port 5000. Now we need to add to the `back/.env` file the following environment variable:

```plaintext
VLLM_ENDPOINT_URL=http://localhost:5000/v1/
```

Now we can start creating the components for the RAG:

1. Let's start by creating the retriever. Go to the admin and click on the AI Configuration section. Then click on the "Retrievers" tab and add a new retriever. For the retriever type select `ColBERT` and for the model name write `colbert-ir/colbertv2.0`. Put `colbert_english` as the name and click on "Save".
2. Go to the generation configurations tab and add a new generation configuration. For the generation configuration select the default values, for the name put `default_gen_config` and click on "Save".
3. Go to the LLM tab and add a new LLM. For the LLM type select `vllm` and for the model name write `TheBloke/zephyr-7B-beta-AWQ`. Put `zephyr_7b` as the name and click on "Save".
4. Go to the prompt tab and add a new prompt. As the system prefix you can copy and paste the system prompt below. Put `chatfaq_prompt` as the name and click on "Save". The system prompt is:

```plaintext
- ChatFAQ is a Open-source RAG framework for deploying LLMs in enterprises
- Your task is to provide an answer based on the information extracts only. Never provide an answer if you don't have the necessary information in the relevant extracts.
- If the question is not about ChatFAQ, politely inform them that you are tuned to only answer questions about ChatFAQ.
```

5. Finally, go to the RAG tab and add a new RAG. For the name put `default` and for the retriever, generation configuration, LLM and prompt select the ones that we created before. Click on "Save".
6. Now, so the RAG can work, we need to index the knowledge base. In the RAG tab you can see an `index` button, when you click on it a new task will be created and the knowledge base will be indexed. After the task is finished you can start using the RAG, wait a few seconds so the RAG is loaded and then you can start asking questions where you deployed your widget.
