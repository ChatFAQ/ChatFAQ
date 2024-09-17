# ChatFAQ Command Line Interface (CLI) Tool

> ⚠️ The CLI is currently not being maintained, we don't recommend using it.

The CLI allows you to interact with the backend server from the command line. It offers the same capabilities as the Django admin panel or the ChatFAQ admin.

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
