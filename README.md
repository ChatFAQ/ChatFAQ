## [![Group 403 (1)](https://github.com/ChatFAQ/ChatFAQ/assets/127191313/445f5cf9-c557-4529-9d94-a61839d3bb83)](https://www.chatfaq.io/) - An Open Source RAG & Agent ecosystem for your business needs

**ChatFAQ** is an open-source platform and framework for creating diverse AI-powered conversational solutions:

- LLM-based chatbots
- RAG-enhanced chatbots
- Agentic workflows
- Rule-based Finite State Machines with LLM assistance
- Hybrid solutions combining multiple approaches

**ChatFAQ** fully relies on **open-source technologies**, allowing for flexibility, privacy, full control and costs-effectiveness.

It includes a SDK **to build your specialized NLG engine** and customized chat widgets,
ensuring a tailored experience for users and avoiding vendor lock-in.

https://github.com/ChatFAQ/ChatFAQ/assets/127191313/7927f51f-d7ac-40e5-b4d0-62081742de4f

### Documentation

The official documentation is hosted on [Read the Docs](https://chatfaq.readthedocs.io/en/latest/).

### Components

![ChatFAQ Components](doc/source/_static/images/chatfaq_components.png)

- **ChatFAQ SDK**: A SDK to build agents, RAG pipelines, Finite State Machines and any other AI flow you can imagine.
- **Chat Widget**: Embed a customizable chat interface into your website.
- **Admin Dashboard**: A dashboard to manage all your knowledge bases, LLMs, retrievers, label conversations, see statistics, etc.
- **Ray Cluster**: Power indexing pipelines, LLM inference, retrieval operations and more.
- **Backend**: Django-based system to orchestrate all components.
- **Foundational Models**:

  - Primary: vLLM integration for open-source LLMs
  - Additional: Integrations with OpenAI, Anthropic, Mistral, Gemini and Together.

### Visit Us!

For more information about ChatFAQ and any additional needs, feel free to visit our [website](https://www.chatfaq.io/)

Or chat with us on [Discord](https://discord.gg/MTWF4SRc3M) for any requests or inquiries about this repository. <img src="https://github.com/ChatFAQ/ChatFAQ/assets/127191313/0a400677-c938-4143-8533-2551b0158f52" alt="logo_discord" width="25"/>


<div align="center">
  <img src="https://assets-global.website-files.com/649164df52b043f1d5307b14/660d2f3981e7b29eba28b6e0_CONBANDERA_KITDIGITAL%20(1)-p-1600.png" alt="logo_redes">
</div>

### Examples

Here are some examples of how to use the ChatFAQ SDK to build different types of conversational solutions:

- **LLM Example**: This example demonstrates a simple chatbot using an LLM to generate responses. [fsm_definition.py](sdk/examples/llm_example/fsm_definition.py)
- **RAG Example**: This example shows how to build a chatbot that uses Retrieval-Augmented Generation (RAG) to provide more informed answers. [fsm_definition.py](sdk/examples/rag_example/fsm_definition.py)
- **Feedbacks Example**: This example shows how to collect user feedback using star ratings and text inputs. [fsm_definition.py](sdk/examples/feedbacks_example/fsm_definition.py)
- **Full KB RAG Example**: This example demonstrates how to use the entire knowledge base for RAG and prompt caching, which can be useful given that context windows are large and we don't have to deploy a retriever. [fsm_definition.py](sdk/examples/full_kb_rag_example/fsm_definition.py)
- **Retrieve Example**: This example shows how to use the `retrieve` function to fetch relevant information from a knowledge base. [fsm_definition.py](sdk/examples/retrieve_example/fsm_definition.py)
- **Structured Generation Example**: This example shows how to use the LLM to extract structured information from user input. [fsm_definition.py](sdk/examples/structured_generation/fsm_definition.py)
