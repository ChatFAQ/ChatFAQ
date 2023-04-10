# ChatFAQ SDK

This SDK assists you on 2 main tasks:

- Creating FSM Definitions on a ChatFAQ's back-end server

- Hosting RPCs (Remote Procedure Calls) to serve when a session's FSM connected to a ChatFAQ's back-end server reach the call.

## Installation/Documentation

https://with-chatfaq.readthedocs-hosted.com/en/latest/modules/sdk/index.html


## Build the docs

go inside the `doc` directory and run:

```
poetry run make html
```

## Publish package on PYPI test

add repository to poetry config

    poetry config repositories.chatfaq-sdk https://test.pypi.org/legacy/

get token from https://test.pypi.org/manage/account/token/

store token using

    poetry config pypi-token.chatfaq-sdk pypi-YYYYYYYY
