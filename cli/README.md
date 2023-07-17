# ChatFAQ Command Line Interface (CLI) Tool

The full potential of ChatFAQ services, datasets, and models at the tip of your fingers.

## Prerequisites

Make sure the next list of packages are installed on your system:

- Python 3.10
- poetry

## Installation

### Local build

`poetry install`

### PYPI

`poetry add chatfaq-cli`

## Usage

First of all you should configure the remote target server:

`chatfaq config host <REMOTE_ADRESS>`

Then you can log in into the remote server:

`chatfaq config auth <TOKEN>`

You can obtain this token by login into http://localhost:8000/back/api/login/ with an admin user.

## Commands

`chatfaq --help`
