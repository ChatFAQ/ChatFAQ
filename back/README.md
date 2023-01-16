# Riddler Back

This project hold the [FSM](riddler/apps/fsm/lib/__init__.py) (Finite State Machine) and the Broker of the Riddler project, it can be considered the Back-end of riddler.

It also serves a very simple dummy [Front-end](riddler/back/riddler/apps/broker/templates/chat/index.html) just as an example of a WS connection to the backend from a custom widget.

## Installation

Three options to run this project: docker, local.

### 1. Docker Compose


As simple as running

`docker-compose up`

### 3. Set it up locally

Install machine requirements:

- Python 3.10
- python3.10-dev
- python3.10-distutils
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

Apply django fixtures

`make apply_fsm_fixtures`

Create a superuser

`./manage.py createsuperuser`

Run the server

`make run`


## Telegram

If you want to test the Telegram platform you should obtain a Telegram token from a bot and run your service under https using, for example, ngrok `ngrok http 8000`.

Then run docker-compose:

`BASE_URL=<HTTPS_ADDRESS> docker-compose up`

Or if you are running it straight in you machine make sure to include in your .env

`BASE_URL=<HTTPS_ADDRESS>`

The in your admin go to Platform bots: http://localhost:8000/back/admin/broker/platformbot/ and create a new one selecting your desired FSM, Platform type = Telegram and in platform meta something as:

```
{
    "token": <TELEGRAM_TOKEN>,
    "api_url": "https://api.telegram.org/bot",
}
```


## Endpoints

Dummy chat: http://localhost:8000/back/api/broker/chat/

Admin: http://localhost:8000/back/admin/

Swagger Docs: http://localhost:8000/back/api/schema/swagger-ui/

Redoc Docs: http://localhost:8000/back/api/schema/redoc/


## Build the docs

go inside the `doc` directory and run:

```
poetry run make html
```
