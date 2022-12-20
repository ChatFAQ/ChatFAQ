# Riddler Back

This project hold the [FSM](api/fsm) (Finite State Machine) and the [Broker](api/broker) of the Riddler project, it can be considered the Back-end of riddler.

It also serves a very simple dummy [Front-end](api/broker/templates/chat/index.html) just for testing the WS connection to the backend from a custom widget.

## Installation

Three options to run this project: docker, pypi, local.

### 1. Docker Compose


As simple as running

`docker-compose up`

<hr style="border:1px solid gray">

If you want to test the Telegram platform you should obtain a Telegram token from a bot and run your service under https using, for example, ngrok `ngrok http 8000`.

Then run docker-compose:

`TG_TOKEN=<TOKEN> BASE_URL=<HTTPS_ADDRESS> docker-compose up`

### 2. From pip repository

We still have not deployed a public stable first release to pypi

### 3. Set it up locally

Install machine requirements:

- Python 3.10
- PostgreSQL
- gdal-bin
- poetry

Create a .env file with the needed variables set. You can see an example of those on [.env_example](.env_example)

This project is based on [Model-W](https://github.com/ModelW/project-maker) therefore we use poetry for the management of the dependencies

Go inside ./back directory Create and install project dependencies:

`poetry install`

Activate the virtual environment

`poetry shell`

Create a 'riddler' database in postgres

`sudo -u postgres psql -c "CREATE DATABASE riddler"`

Create a 'riddler' user in postgres

`sudo -u postgres psql -c "CREATE user riddler WITH encrypted password 'riddler';"`

Grant to the newly created user the proper the privileges to the database

`sudo -u postgres psql -c "grant all privileges on database riddler to riddler;"`

Apply django migrations

`./manage.py migrate`

Apply django fixtures

`make apply_fsm_fixtures`

Create a superuser

`./manage.py createsuperuser`

Run the server

`make run`

## Endpoints

Dummy chat: http://localhost:8000/back/api/broker/chat/

Admin: http://localhost:8000/back/admin/

Swagger Docs: http://localhost:8000/back/api/schema/swagger-ui/

Redoc Docs: http://localhost:8000/back/api/schema/redoc/
