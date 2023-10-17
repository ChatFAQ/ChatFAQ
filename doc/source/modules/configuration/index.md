# Model Configuration

After setting up the components, you will probably want to configure a model that you want to use for your chatbot. Typically the model will be used from the SDK, from a state within its FSM.

## The RAG Pipeline

The [RAG (Retrieval-Augmented Generation)](https://arxiv.org/abs/2005.11401) architecture is a workflow that combines a retriever and a generator. The retriever is used to retrieve the most relevant knowledge items from a knowledge base, and the generator is used to generate an answer from the retrieved knowledge items.

In ChatFAQ we choose to follow this pattern. Next we explain how to configure it.

We define 5 main components that are needed to configure a RAG pipeline:

- Knowledge Base
- Retriever
- Prompt
- Generation
- LLM
- RAG

ChatFAQ provide in its fixtures a default configuration for each of these components except for the Knowledge Base and the RAG Config. You can apply the fixtures by simply running the following command from the `back` directory:

```bash
make apply_fixtures
```

Currently all the relevant data/models can be accessed and modified from the Django admin panel ([http://localhost/back/admin/](http://localhost/back/admin/)) or from the CLI.


### Knowledge Base

The knowledge base is your source of truth.

It typically starts with a collection of documents (CSVs, PDFs or URLs) that the chatbot will use to answer questions.

Once a knowledge base is created, the system will parse your source document and generate the corresponding knowledge items.

Next we list the different properties that a of knowledge bases has.

- lang: The language of the knowledge base. It is used to tokenize the documents.

- original_csv: The CSV file.
- original_pdf: The PDF file.
- original_url: The URL.

###### CSV parsing options
- csv_header: Whether the CSV file has a header or not.
- title_index_col: The index of the column that contains the title of the knowledge item.
- content_index_col: The index of the column that contains the content of the knowledge item.
- url_index_col: The index of the column that contains the URL of the knowledge item.
- section_index_col: The index of the column that contains the section of the knowledge item.
- role_index_col: The index of the column that contains the role of the knowledge item.
- page_number_index_col: The index of the column that contains the page number of the knowledge item.

###### PDF parsing options
- strategy: The strategy to use to parse the pdf file. Can be 'auto', 'fast', 'ocr' or 'high_res'.
###### URL parsing options
- recursive: Whether to recursively parse the URLs or not.
###### PDF & URL parsing options
- splitter: The splitter used to split the documents into chunks. It is used to generate the knowledge items.
- chunk_size: The number of tokens per chunk. It is used by the splitter to split the documents into chunks. The bigger the chunk size, the more memory the system will need to parse the documents.
- chunk_overlap: The number of tokens that overlap between two chunks. It is also used by the splitter

### Retriever Config

The retriever is the component that will retrieve the most relevant knowledge items from the knowledge base.

The retriever is configured with the following properties:

- name: Just a name for the retriever.
- model_name: The name of the retriever model to use. It must be a HuggingFace repo id.
- batch_size: The batch size to use for the retriever.
- device: The device to use for the retriever. It can be a CPU or a GPU.


### Prompt Config
The prompt is the input that the LLM will use to generate the answer. It is composed of the following parts:

- name: Just a name for this prompt.
- system_prefix: The prefix to indicate instructions for the LLM.
- system_tag: The tag to indicate the start of the system prefix for the LLM.
- system_end: The tag to indicate the end of the system prefix for the LLM.
- user_tag: The tag to indicate the start of the user input.
- user_end: The tag to indicate the end of the user input.
- assistant_tag: The tag to indicate the start of the assistant output.
- assistant_end: The tag to indicate the end of the assistant output.
- n_contexts_to_use: The number of contexts to use.

### Generation Config
The generation config is used to define the characteristics of the second part from the RAF pipeline, the generation process.

The generation process is configured with the following properties:

- name: Just a name for the generation process.
- top_k: The number of tokens to consider for the top-k sampling.
- top_p: The cumulative probability for the top-p sampling.
- temperature: The temperature for the sampling.
- repetition_penalty: The repetition penalty for the sampling.
- seed: The seed for the sampling.
- max_new_tokens: The maximum number of new tokens to generate.
- model: The model this generation configuration belongs to.

### LLM Config
The LLM is the component that defines the model that will generate the answer from the prompt.

The LLM is configured with the following properties:

- name: Just a name for the LLM.
- llm_type: The type of LLM to use. It can be 'openai', 'huggingface', etc.
- llm_name: The name of the LLM to use. It can be a HuggingFace repo id, an OpenAI model id, etc.
- ggml_llm_filename: The GGML filename of the model, if it is a GGML model.
- model_config: The huggingface model config of the model, needed for GGML models.
- load_in_8bit: Whether to load the model in 8bit or not.
- use_fast_tokenizer: Whether to use the fast tokenizer or not.
- trust_remote_code_tokenizer: Whether to trust the remote code for the tokenizer or not.
- trust_remote_code_model: Whether to trust the remote code for the model or not.
- revision: The specific model version to use. It can be a branch name, a tag name, or a commit id, since we use a git-based system for storing models
- model_max_length: The maximum length of the model.


### RAG Config
Finally, the RAG config is used to glue all the previous components together.

It relates the different elements to create a RAG (Retrieval Augmented Generation) pipeline.

The RAG config is configured with the following properties:

- name: Just a name for the RAG config.
- knowledge_base: The knowledge base to use.
- llm_config: The LLM config to use.
- prompt_config: The prompt config to use.
- generation_config: The generation config to use.
- retriever_config: The retriever config to use.



Remember thatcurrently all the relevant data/models can be accessed and modified from the Django admin panel ([http://localhost/back/admin/](http://localhost/back/admin/)) or from the CLI.

## Using your RAG Pipeline

Once you have created your RAG pipeline, you can use it to generate answers.

How? well, you just need to reference the name of the Rag Config from a state of your SDK's FSM. <a href="/en/latest/modules/sdk/index.html#model-example">Here is an example of that</a>
