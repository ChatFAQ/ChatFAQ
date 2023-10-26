# Introduction

## Installation

The system comprises three main components that you need to install:


![ChatFAQ Components](./_static/images/chatfaq_components.png)


- The Back (<a href="/en/latest/modules/installations/index.html#back-installation">local install</a>) manages the communication between all the components. It also houses the database for storing all the data related to the chatbots, datasets, models, etc...


- The SDK (<a href="/en/latest/modules/installations/index.html#sdk-installation">local install</a>) launches a Remote Procedure Call (RPC) server to execute transitions and events from the posted FSM definitions.


- The Widget (<a href="/en/latest/modules/installations/index.html#widget-installation">local install</a>) is a JS browser client application from which the user interacts with the bot.

### Docker Compose

There is a `docker-compose.yaml` that runs all the the services you need. You can run it with:

First of all we recommend to add to your hosts file (usually under `/etc/hosts`) the following lines in order to share the `.env` files values between a local deployment and a docker deployment:

    127.0.0.1  postgres
    127.0.0.1  back
    127.0.0.1  redis

Then you need to create the corresponding `.env` files for each service. You can see an example of those on:

- [back/.env_example](https://github.com/ChatFAQ/ChatFAQ/blob/develop/back/.env_example)
- [sdk/.env_example](https://github.com/ChatFAQ/ChatFAQ/blob/develop/sdk/.env_example)
- [widget/.env_example](https://github.com/ChatFAQ/ChatFAQ/blob/develop/widget/.env_example)


Now you can run the migrations and the fixtures for the initial database data:

    docker compose -f docker-compose.yaml -f docker-compose.vars.yaml run back poetry run ./manage.py migrate
    docker compose -f docker-compose.yaml -f docker-compose.vars.yaml run back poetry run make apply_fixtures

Create a superuser on the backend (making sure you answer 'yes' to the question 'Belongs to the RPC group?')

    docker compose -f docker-compose.yaml -f docker-compose.vars.yaml run back poetry run ./manage.py createsuperuser

Generate a ChatFAQ Token with the user and password you just created:

    docker compose -f docker-compose.yaml -f docker-compose.vars.yaml run back curl -X POST -u <USER>:<PASSWORD> http://back:8000/back/api/login/

Which will respond something as such:

    {"expiry":null,"token":"<TOKEN>"}

Add it to your `sdk/.env` file:

    CHATFAQ_TOKEN=<TOKEN>

And finally, now you can run all the services:

    docker compose -f docker-compose.yaml -f docker-compose.vars.yaml up -d


## Model Configuration

After setting up the components, you will probably want to configure a model that you want to use for your chatbot. Typically the model will be used from the SDK, from a state within its FSM.

Here is an example of a minimum model ([configuration](./modules/configuration/index.md))

## Quick Start

Learning <a href="/en/latest/modules/sdk/index.html#usage">how to use the SDK</a> is the only requirement to start building your own chatbots with ChatFAQ.
