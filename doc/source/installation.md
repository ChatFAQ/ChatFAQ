# Installation

## Components

The system comprises seven main components, here are their relationships and the technologies they are built with:


![ChatFAQ Components](./_static/images/chatfaq_components.png)


- **Back-end** <!-- (<a href="/en/latest/modules/installations/index.html#back-installation">local install</a>) --> manages the communication between all the components. It also houses the database for storing all the data related to the chatbots, datasets, models, etc...


- **SDK** <!-- (<a href="/en/latest/modules/installations/index.html#sdk-installation">local install</a>) --> launches a Remote Procedure Call (RPC) server to execute transitions and events from the posted FSM definitions.


- **Widget** <!-- (<a href="/en/latest/modules/installations/index.html#widget-installation">local install</a>) --> is a JS browser client application from which the user interacts with the bot.


- **Admin** is a JS browser client application to manage the chatbots, datasets, retriever, models, RAG configs, etc...


- **Ray workers** are used to run distributed inference on the models.


- **Channel layer** (Redis) is used to communicate through WebSockets between the back-end and the SDK, admin and widget.


- **Relational Database** (PostgreSQL) is used to store all the data related to the chatbots, datasets, retriever, models, RAG configs, etc...

### Docker

Before running the services, ensure you have <a href="https://docs.docker.com/engine/install/" target="_blank">Docker</a> and  <a href="https://docs.docker.com/compose/" target="_blank">Docker Compose</a> installed on your system. You can install them using the following instructions:

We prepared you a `docker-compose.yaml` that set up all the services for you. You can find it on the root of the repository.

#### Configuration Instructions

But first you add to your hosts file (usually under `/etc/hosts`) the following lines in order to share the `.env` files values between a local deployment and a docker deployment:

127.0.0.1  postgres
127.0.0.1  back
127.0.0.1  redis

Then you need to create the corresponding `.env` files for each service. You can see an example of those on:

- [back/.env-template](https://github.com/ChatFAQ/ChatFAQ/blob/develop/back/.env-template)
- [sdk/.env-template](https://github.com/ChatFAQ/ChatFAQ/blob/develop/sdk/.env-template)
- [admin/.env-template](https://github.com/ChatFAQ/ChatFAQ/blob/develop/admin/.env-template)
- [widget/.env-template](https://github.com/ChatFAQ/ChatFAQ/blob/develop/widget/.env-template)


Now you can run the migrations and the fixtures for the initial database data:

    docker compose -f docker-compose.yaml -f docker-compose.vars.yaml run back poetry run ./manage.py migrate
    docker compose -f docker-compose.yaml -f docker-compose.vars.yaml run back poetry run make apply_fixtures

Create a superuser on the backend (making sure you answer 'yes' to the question 'Belongs to the RPC group?')

    docker compose -f docker-compose.yaml -f docker-compose.vars.yaml run back poetry run ./manage.py createsuperuser

Generate a ChatFAQ Token with the user and password you just created:

    docker compose -f docker-compose.yaml -f docker-compose.vars.yaml run back poetry run ./manage.py createtoken <USER>

Which will respond something as such:

    Token for user <USER> created: <TOKEN>

Add it to your `sdk/.env` file:

    CHATFAQ_TOKEN=<TOKEN>

and the `back/.env` file:

    BACKEND_TOKEN=<TOKEN>

The configuration we provided for the LLM uses an OpenAI model. To use it, you need to add your OpenAI API key to the `back/.env` file:

    OPENAI_API_KEY=<API_KEY>

Don't worry, our solution supports any other LLM model. It also supports deploying your own local model on a VLLM server. However, for simplicity and because OpenAI models are the most popular, we are using an OpenAI model as the default.

#### Running the Services

To start all the services, run the following command:

    docker compose -f docker-compose.yaml -f docker-compose.vars.yaml up

Congratulations! You now have a running ChatFAQ instance.

#### Accessing the Chatbot

You can interact with the chatbot by navigating to:

<a href="http://localhost:3003/demo/" target="_blank">http://localhost:3003/demo/</a>

To manage the chatbot and view the model configuration we provided, go to:

<a href="http://localhost:3000" target="_blank">http://localhost:3000</a>

## Deeper into ChatFAQ

If you want to use your own dataset, you can check the [Dataset Configuration](./modules/configuration/index.html#knowledge-base) documentation.

If you want to learn how to configure your own RAG (LLM model, retriever model, prompt configuration, etc...) you can check the [RAG Configuration](./modules/configuration/index.html#rag-config) documentation.

If you want to learn how to use the SDK, so you can create your own chatbot behavior, you can check the [SDK](./modules/sdk/index.md) documentation.
