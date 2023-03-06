# ChatFAQ Back

This project hold the [FSM](back/apps/fsm/lib/__init__.py) (Finite State Machine) and the Consumers of the ChatFAQ project

## Installation/Documentation

https://with-chatfaq.readthedocs-hosted.com/en/latest/modules/back/index.html


## Endpoints

Custom WS chat: http://localhost:8000/back/api/broker/chat/

Admin: http://localhost:8000/back/admin/

Swagger Docs: http://localhost:8000/back/api/schema/swagger-ui/

Redoc Docs: http://localhost:8000/back/api/schema/redoc/


## Build the docs

go inside the `doc` directory and run:

```
poetry run make html
```
