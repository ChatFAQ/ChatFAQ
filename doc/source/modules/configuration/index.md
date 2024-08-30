# AI Configuration

## Table of Contents
- [AI Configuration](#ai-configuration)
  - [Table of Contents](#table-of-contents)
    - [Knowledge Base](#knowledge-base)
      - [CSV parsing options](#csv-parsing-options)
      - [PDF and URL parsing options](#pdf-and-url-parsing-options)
      - [Parsing Recommendations](#parsing-recommendations)
      - [CSV Structure](#csv-structure)
      - [Knowledge items Recomendations](#knowledge-items-recomendations)
    - [Retriever Config](#retriever-config)
      - [Model properties](#model-properties)
      - [Knowledge Base properties](#knowledge-base-properties)
      - [Model inference properties](#model-inference-properties)
      - [ColBERT Search](#colbert-search)
      - [Standard Semantic Search](#standard-semantic-search)
      - [Indexing](#indexing)
    - [LLM Config](#llm-config)
      - [OpenAI](#openai)
      - [vLLM Client](#vllm-client)
    - [Prompt Config](#prompt-config)
        - [Description of the assistant](#description-of-the-assistant)
        - [Refusals to out of scope questions](#refusals-to-out-of-scope-questions)
    - [Generation Config](#generation-config)
  - [Using your AI Components](#using-your-ai-components)


Here you can set up multiple AI components that can be used to compose AI pipelines using Finite State Machines from the ChatFAQ SDK. For example:

- You can create a RAG (Retrieval Augmented Generation) FSM pipeline, using a retriever, a generator and a knowledge base.
- You can create a simple chatbot using only a LLM.
- You can create any kind of agent using the ChatFAQ SDK, given that the backend supports tool use.

ChatFAQ provide in its fixtures a default configuration for each of these components. You can apply the fixtures by simply running the following command from the `back` directory:

```bash
make apply_fixtures
```

We also provide an example of each component here, so you can use it as a reference.

Currently all the relevant data/models can be accessed and modified from the Django admin panel ([http://localhost/back/admin/](http://localhost/back/admin/)) or from the CLI.

### Knowledge Base

The knowledge base is your source of truth.

It typically starts with a collection of documents (CSVs, PDFs or URLs) that the chatbot will use to answer questions.

Once a knowledge base is created, the system will parse your source document and generate the corresponding knowledge items.

Next we list the different properties that a of knowledge bases has.

- **lang**: The language of the knowledge base. It is used to tokenize the documents.
- **original_csv**: The CSV file.
- **original_pdf**: The PDF file.
- **original_url**: The URL.

#### CSV parsing options

- **csv_header**: Whether the CSV file has a header or not.
- **title_index_col**: The index of the column that contains the title of the knowledge item.
- **content_index_col**: The index of the column that contains the content of the knowledge item.
- **url_index_col**: The index of the column that contains the URL of the knowledge item.
- **section_index_col**: The index of the column that contains the section of the knowledge item.
- **role_index_col**: The index of the column that contains the role of the knowledge item.
- **page_number_index_col**: The index of the column that contains the page number of the knowledge item.
- **source_index_col**: The index of the column that contains the original document of the knowledge item.

#### PDF and URL parsing options

- **strategy**: The strategy for parsing PDF files using [unstructured.io](https://github.com/Unstructured-IO/unstructured-api), which is a powerful and versatile library for extracting information from unstructured data sources, can be set to `auto`, `fast`, `ocr_only`, or `high_res`, with the default being `fast` (for more detailed information and documentation on these strategies and their applications, you can visit the following [link](https://github.com/Unstructured-IO/unstructured-api?tab=readme-ov-file#strategies) ).
  - `auto` : It will determine when a page can be extracted using `fast` or `ocr_only mode`, otherwise it will fall back to `hi_res`
  - `ocr_only` : This strategy runs the document through Tesseract for OCR (Optical Character Recognition).
  - `high_res`: It is the better choice for PDFs that may have text within embedded images, or for achieving greater precision of element          types in the response JSON. Please be aware that, as of writing, `hi_res` requests may take 20 times longer to process compared to         the `fast` option.
  - `fast`: is the default strategy and works well for documents that do not have text embedded in images.
- **recursive**: Whether to recursively parse the URLs or not. Default: True.
- **splitter**: The splitter used to split the documents into chunks. It is used to generate the knowledge items. Can be 'sentences', 'words', 'tokens' and 'smart'. Default: 'sentences'.
- **chunk_size**: The number of tokens per chunk. It is used by the splitter to split the documents into chunks. Default: 128.
- **chunk_overlap**: The number of tokens that overlap between two chunks. Default: 16.

#### Parsing Recommendations

- The **strategy** to use depends on the time that you want to wait for the parsing process to finish and the quality of the parsing process. The strategies are ordered from fastest to slowest and from worst quality to best quality. The 'fast' strategy is the default one and it is the one that we recommend for most use cases, it only lasts a few seconds and it has a good quality. The 'high_res' strategy is the one with the best quality but it can last several minutes. For more information about the different strategies check [here](https://unstructured-io.github.io/unstructured/bricks/partition.html#partition-pdf).

- The **splitter** that we recommend is the 'sentences' one. It splits the documents into sentences and then it merges the sentences into chunks of approximately 'chunk_size' tokens. This is the best option for most use cases. The 'smart' splitter uses GPT-4 to split the documents into semantic meaningful chunks, this is **VERY EXPENSIVE** and can bump into OpenAI rate limits (will be optimized in the future).

- The **chunk_size** that we recommend is 128. This is the default value and it is the one that we recommend for most use cases, it is a good balance between retrieval quality and information density. If you want to increase the retrieval quality you can decrease this value, but it will decrease the information density of a chunk.

- The **chunk_overlap** is used when splitting with the 'words' or 'tokens' splitters. 16 or 32 is enough for not losing information between chunks.

#### CSV Structure

An example of a CSV for the Knowledge Base is the following:

| title | content | url | section | role |
| --- | --- | --- | --- | --- |
| Can ChatFAQ integrate with communication tools like Slack and Teams? | Yes, ChatFAQ can integrate with communication tools like Slack and Teams, enhancing your communication capabilities and enabling seamless interactions with your audience. | <https://www.chatfaq.io/features/integrations> | Features > Integrations | user |
| Can the ChatFAQ Widget be tailored to fit specific brand identities? | Absolutely, the ChatFAQ Widget can be fully branded to reflect your brand's uniqueness, including size, color, fonts, and logo. This ensures it aligns perfectly with your brand identity. | <https://www.chatfaq.io/features/widget> | Features > Widget | user |
| Does ChatFAQ offer a customized Natural Language Processing (NLP) engine? | Yes, ChatFAQ includes a specialized NLP/NLG engine that enhances the conversational capabilities of chatbots, making them more effective in understanding and responding to user queries. | <https://github.com/ChatFAQ/ChatFAQ> | GitHub > Documentation | user |
| Does ChatFAQ offer specific enterprise solutions? | Indeed, ChatFAQ is suitable for businesses and can be tailored to meet enterprise needs. It offers features and customization options suitable for businesses of all sizes. | <https://github.com/ChatFAQ/ChatFAQ> | GitHub > About | user |
| Does the ChatFAQ Widget support multiple languages? | Yes, the ChatFAQ Widget is multilingual, allowing businesses to communicate with a global customer base while maintaining service quality. | <https://www.chatfaq.io/features/widget> | Features > Widget | user |
| How can I customize the user interface of the ChatFAQ Widget? | The ChatFAQ Widget offers complete flexibility over UI aspects, including size, color, fonts, and logo, to align with your brand's uniqueness and cater to your audience's needs. | <https://www.chatfaq.io/features/widget> | Features > Widget | user |
| How can I expand my knowledge dataset with ChatFAQ? | You can expand your knowledge dataset with ChatFAQ by uploading your business content as CSV or PDF files. ChatFAQ will automatically generate utterances to enhance your knowledge dataset, improving the accuracy of the AI model. Even if you don't have existing Frequently Asked Questions, ChatFAQ can infer FAQs and prepare a training dataset covering your business context. | <https://www.chatfaq.io/features/generative-ai> | Features > Generative AI | user |
| ... | ... | ... | ... | ... |

#### Knowledge items Recomendations

**Title Column**

- Semantically Descriptive: Ensure that the title of each knowledge item is semantically descriptive. It should clearly and accurately reflect the content within.
- Uniqueness: Each title should be unique within the knowledge base. This uniqueness aids in distinguishing between different knowledge items and helps in efficient retrieval.

**Content Column**

- Markdown Format: Content can be formatted in Markdown. This allows for structured and visually appealing presentation of information.
- Prompt Reinforcement: When integrating content, reinforce the prompt by indicating to the model that it is capable of interpreting Markdown. This can enhance the model's ability to process and understand the content effectively.
- Balanced Length: The content of each knowledge item should neither be too short nor excessively long. Aim for a balanced length to provide sufficient detail without overwhelming.
- Consistency in Size: Strive for a consistent size among different knowledge items. This balance helps in the optimal functioning of the retriever mechanism, as it ensures a uniformity in the information density and retrieval times.

### Retriever Config

The retriever is the component that will retrieve the most relevant knowledge items from the knowledge base.

The retriever is configured with the following properties, which can be separated into 3 groups:

- **Model properties**: These are the properties that define the retriever model.
- **Knowledge Base properties**: These are the properties that define the knowledge base.
- **Model inference properties**: These are the properties that define the inference properties of the retriever.

#### Model properties
- **name**: Just a name for the retriever.
- **model_name**: The name of the retriever model to use. It must be a HuggingFace repo id. Default: 'colbert-ir/colbertv2.0'.
- **retriever_type**: The type of retriever to use. It can be 'ColBERT Search' or 'Standard Semantic Search'. Default: 'ColBERT Search'.

#### Knowledge Base properties
- **knowledge_base**: The knowledge base to use for the retriever.
- **index_status**: The status of the retriever index.
- **s3_index_path**: The path to the retriever index in S3.

#### Model inference properties
- **batch_size**: The batch size to use for the retriever. Default: 1.
- **device**: The device to use for the retriever. It can be a CPU or a GPU. Default: 'cpu'.
- **enabled**: Whether the retriever is enabled. Default: True.
- **num_replicas**: The number of replicas to deploy in the Ray cluster. Default: 1.

#### ColBERT Search

We recommend setting [ColBERT](https://arxiv.org/abs/2004.12832) as the retriever. It generates multiple embeddings for each knowledge item and query, which allows for more accurate retrieval generally. The search process is faster than the Standard Semantic Search retriever, but the indexing process is slower.

Model per language:

- English: [colbert-ir/colbertv2.0](https://huggingface.co/colbert-ir/colbertv2.0)
- French: [antoinelouis/colbertv1-camembert-base-mmarcoFR](https://huggingface.co/antoinelouis/colbertv1-camembert-base-mmarcoFR)
- Spanish: [AdrienB134/ColBERTv2.0-spanish-mmarcoES](https://huggingface.co/AdrienB134/ColBERTv2.0-spanish-mmarcoES)

#### Standard Semantic Search

We recommend setting the **model_name** to one of the [e5 family models](https://huggingface.co/intfloat). This retriever is developed with these models as the base, so it will work better with them.

Model per language:

- English: [intfloat/e5-small-v2](https://huggingface.co/intfloat/e5-small-v2)
- Other languages: [intfloat/multilingual-e5-small](https://huggingface.co/intfloat/multilingual-e5-small)

For **batch_size** we recommend using 1 for CPU and for GPU as much as your GPU can handle. For personal use, batch size of 1 is enough, but for production use, you should use a higher batch size and a GPU.

For **device** we recommend using a GPU if you have one available. For personal use it is enough to use a CPU, but for production use, you should use a GPU.

An example of a retriever config is the following:

```json
{
    "name": "colbert",
    "model_name": "colbert-ir/colbertv2.0",
    "retriever_type": "ColBERT Search",
    "knowledge_base": 1,
    "index_status": "NO_INDEX",
    "s3_index_path": "",
    "batch_size": 1,
    "device": "cpu",
    "enabled": true,
    "num_replicas": 1
}
```

#### Indexing

The retriever needs to build an index of the knowledge base to perform searches. This index is created and managed automatically, but you need to manually trigger indexing.

In the admin panel, each Retriever has a "ReIndex" button. This button is active (clickable) when:

1. The index has not been built yet (index_status is NO_INDEX)
2. The index is outdated (index_status is OUTDATED)

The index status will automatically update to OUTDATED when:

- The associated knowledge base is modified
- The retriever's model or type is changed

To initiate indexing:

1. Go to the admin panel.
2. Navigate to the Retrievers section
3. Find the retriever you want to index
4. Click the "ReIndex" button if it's active

The indexing process will start a ray task in the background. You can monitor its progress in the Ray dashboard. Once complete, the index status will update to UP_TO_DATE.

For ColBERT retrievers, the index is stored in S3 for persistence and faster loading. The S3 path is automatically generated and stored in the `s3_index_path` field.

Note: Indexing can take some time, especially for large knowledge bases. Ensure your system has sufficient resources available before starting the process.


### LLM Config

The LLM is the component that defines the model that will generate the answer from the prompt.

The LLM is configured with the following properties:

- **name**: Just an identifier name for the LLM.
- **llm_type**: The type of LLM to use. It can be 'OpenAI', 'Claude', 'Mistral', 'Together' or 'vLLM Client'. Default: 'OpenAI'.
- **llm_name**: The API name of the LLM to use. It is the HuggingFace repo id if using the vLLM Client, an OpenAI model api name if using OpenAI, etc. Default: gpt-4o.
- **base_url**: The base url where the model is hosted. It is used for vLLM deployments and Together LLM Endpoints as they use the OpenAI API. Default: None.
- **model_max_length**: The maximum length of the model. Default: None.
- **enabled**: Whether the LLM is enabled. Default: True.
- **num_replicas**: The number of replicas to deploy in the Ray cluster. Default: 1.

Our preferred option is to use an open-source LLM like [Llama-2](https://huggingface.co/meta-llama/Llama-2-7b-chat-hf) for English and [Qwen-Chat](https://huggingface.co/Qwen/Qwen-7B-Chat) for other languages.

To access Llama-2 models you need to set a environment variable in the back `.env` file with your HuggingFace API key:

```
HUGGINGFACE_KEY=XXXXXX
```


#### OpenAI

This is the easiest way to get a model running. We just need to specify the model type and the model name. For example:

```json
{
    "name": "GPT-4o",
    "llm_type": "OpenAI",
    "llm_name": "gpt-4o",
    "enabled": true,
    "num_replicas": 1
}
```

The OpenAI models are specified [here](https://platform.openai.com/docs/models/). To access OpenAI models you need to set a environment variable in the back `.env` file with your OpenAI API key:

```
OPENAI_API_KEY=XXXXXX
```

The same process applies for the other LLM clients. Look at the back `.env-template` file to see how to set the environment variables.

#### vLLM Client

This uses a client to connect to a [vLLM server](https://github.com/vllm-project/vllm). The vLLM server is a server that runs a LLM model and exposes an API to generate answers, it has the best latency and throughput performance.

To configure this server we refer to the [vLLM documentation](https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html).

### Prompt Config

> ⚠️ This config is not currently used anywhere, right now you set the prompts in the FSM definition. In the future you will be able to reference this prompts configs from the FSM definition.


The prompt is the input that the LLM will use to generate the answer. This config indicates how to build the final prompt that the LLM reads.

- **name**: Just a name for this prompt.
- **system_prompt**: This system prompt indicates the LLM how to behave.
- **n_contexts_to_use**: The maximum number of knowledge items that will be appear in the sources. Default: 3

For RAG (Retrieval-Augmented Generation) applications, we recommend using the following system guidelines as a foundation:


##### Description of the assistant

Here you can describe the assistant, its personality, its role, etc. For example:

```
- You are a helpul AI assistant chatbot for ChatFAQ.
- ChatFAQ is a platform enabling a conversational experience for your customers using Large Language Models (LLMs).
- You answer questions only about ChatFAQ.
- Your answers should avoid being vague or off-topic, and your logic and reasoning should be rigorous, intelligent, and defensible.
- You are excited to be able to help the user, but will refuse to do anything that could be considered dangerous.
```

##### Refusals to out of scope questions

Here you can specify what to do when the user asks a question that is out of scope. For example:

```
- Your task is to provide an answer based on the information extracts only. Never provide an answer if you don't have the necessary information in the relevant extracts.
- If the question is not about ChatFAQ, politely inform them that you are tuned to only answer questions about ChatFAQ.
- If you don't have enough information to answer the question, say "I don't have enough information to give you a confident answer" and link to helpful documentation instead. Never try to make up an answer if you aren't provided the information.
```

You can modify this previous text to adapt it to your use case, but it is important to keep the same structure.

### Generation Config

> ⚠️ This config is not currently used anywhere, right now you set the generation parameters in the FSM definition. In the future you will be able to reference this generation configs from the FSM definition.

The generation config is used to define the characteristics of the second part from the RAG pipeline, the generation process. We use sampling to generate the answer.

The sampling generation process is configured with the following properties:

- **name**: Just a name for the generation process.
- **temperature**: The temperature for the sampling. Default: 0.2.
- **seed**: The seed for the sampling. Default: 42.
- **max_tokens**: The maximum number of new tokens to generate. Default: 1024.

We recommend setting the temperature to low values, less than 1.0 because we want the model to be factual, not creative. A very good guide of all this parameters can be found in the [HuggingFace documentation](https://huggingface.co/blog/how-to-generate).


## Using your AI Components

With the ChatFAQ SDK you can reference these AI components when developing your FSM. Let's say we have a retriever called `chatfaq_retriever` and we want to use it in a state. We can do it like this:

```python
from chatfaq_sdk import ChatFAQSDK
from chatfaq_sdk.clients import retrieve
from chatfaq_sdk.layers import Message

async def send_retrieval(sdk: ChatFAQSDK, ctx: dict):
    query = 'What is ChatFAQ?'
    items = await retrieve(sdk, 'chatfaq_retriever', query, top_k=3, bot_channel_name=ctx["bot_channel_name"])
    yield Message(
        '', # Send only the items in the message to be displayed in the chat UI.
        references=items,
    )

```

For a LLM called 'gpt-4o' we can use it in streaming mode like this:

```python
from chatfaq_sdk import ChatFAQSDK
from chatfaq_sdk.clients import llm_request
from chatfaq_sdk.layers import Message, StreamingMessage

async def send_llm_answer(sdk: ChatFAQSDK, ctx: dict):
    # Some messages
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"},
    ]
    generator = llm_request(sdk, 'gpt-4o', use_conversation_context=False, conversation_id=ctx["conversation_id"], bot_channel_name=ctx["bot_channel_name"], messages=messages)
    yield StreamingMessage(generator)
```

Creating a simple RAG pipeline:

```python
from chatfaq_sdk import ChatFAQSDK
from chatfaq_sdk.clients import retrieve, llm_request
from chatfaq_sdk.layers import Message, StreamingMessage
from chatfaq_sdk.utils import convert_mml_to_llm_format

async def send_rag_answer(sdk: ChatFAQSDK, ctx: dict):

    messages = convert_mml_to_llm_format(ctx["conv_mml"][1:])
    last_user_message = messages[-1]["content"]
    
    # Retrieve context
    contexts = await retrieve(sdk, 'chatfaq_retriever', last_user_message, top_k=3, bot_channel_name=ctx["bot_channel_name"])
    
    # Augment prompt with context
    system_prompt = rag_system_prompt
    context_content = "\n".join([f"- {context['content']}" for context in contexts['knowledge_items']])
    system_prompt += f"\nInformation:\n{context_content}"
    messages.insert(0, {"role": "system", "content": system_prompt})
    
    # Generate response
    generator = llm_request(
        sdk,
        "gpt-4o",
        use_conversation_context=False,
        conversation_id=ctx["conversation_id"],
        bot_channel_name=ctx["bot_channel_name"],
        messages=messages,
    )

    yield StreamingMessage(generator, references=contexts)
```
