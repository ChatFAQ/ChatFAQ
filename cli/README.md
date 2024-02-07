# ChatFAQ Command Line Interface (CLI) Tool

The full potential of ChatFAQ services, datasets, and models at the tip of your fingers.

## Prerequisites

Make sure the next list of packages are installed on your system:

- Python 3.10
- poetry/pip

## Installation

### Local build

`poetry install`

### PYPI

`pip install chatfaq-cli`

## Usage

First of all you should configure the remote target server:

`chatfaq config host <REMOTE_ADRESS>`

Then you can log in into the remote back-end server:

`chatfaq config auth <TOKEN>`

You can retrieve the auth token from the backend server:

`curl -X POST -u username:password http://localhost:8000/back/api/login/`

by using an admin's user and password.

## Commands

For a full list of commands and options run:

`chatfaq --help`

## Notes

For the autocompletion to work you should run:

`chatfaq --install-completion`

or run `chatfaq --show-completion` and add the output to your shell's configuration file.

### Publish package

#### PYPI test

add repository to poetry config

    poetry config repositories.chatfaq-cli https://test.pypi.org/legacy/

get token from https://test.pypi.org/manage/account/token/

store token using

    poetry config pypi-token.chatfaq-cli pypi-YYYYYYYY

#### PYPI production

get token from https://pypi.org/manage/account/token/

store token using

    poetry config pypi-token.chatfaq-cli pypi-XXXXXXXX

Each time you need to publish

Bump version

    poetry version prerelease

or

    poetry version patch

#### Poetry Build

    poetry build

#### Poetry Publish

To TestPyPi

    poetry publish -r chatfaq-cli

To PyPi

    poetry publish
