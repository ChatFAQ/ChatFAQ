# Riddler SDK

This SDK assist on 2 main tasks:

- Creating FSM Definitions on a Riddler server
- Hosting RPCs (Remote Procedure Calls) to serve when a session's FSM connected to a Riddler server reach the call.

## Installation

Go inside ./back directory and install project dependencies:

`poetry install`

## Quick start

Inside _test/__init__.py_ you can find a working example of the usage of the SDK.

First of all we import teh FSM Definition we want to create on Riddler

```
from tests.fsm_def import fsm_def
```

If we look into that module we can observe




## Build the docs

go inside the `doc` directory and run:

```
poetry run make html
```
