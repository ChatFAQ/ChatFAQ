Setting it up locally
=====================

Prerequisites
------------------

- Python 3.10
- python3.10-dev
- python3.10-distutils
- PostgreSQL
- gdal-bin
- poetry


Installation
------------------

Navigate inside :code:`./back`

.. module:: back

Create a :code:`.env` file with the needed variables set. You can see an example of those on the :ref:`.env_example <back_env_example>` file

.. literalinclude:: ../../../../back/.env_example

This project is based on `Model-W <https://github.com/ModelW/project-maker>`_. therefore we use poetry for the management of the dependencies

Go inside ./back directory Create and install project dependencies:

.. code-block:: console

    poetry install

Activate the virtual environment

.. code-block:: console

    poetry shell

Create a 'chatfaq' database in postgres

.. code-block:: console

    sudo -u postgres psql -c "CREATE DATABASE chatfaq"

Create a 'chatfaq' user in postgres

.. code-block:: console

    sudo -u postgres psql -c "CREATE user chatfaq WITH encrypted password 'chatfaq';"

Grant to the newly created user the proper the privileges to the database

.. code-block:: console

    sudo -u postgres psql -c "grant all privileges on database chatfaq to chatfaq;"

Apply django migrations

.. code-block:: console

    ./manage.py migrate

Create a superuser

.. code-block:: console

    ./manage.py createsuperuser

When creating the superuser it will ask you if it belongs to the RPC group, it is important to respond yes(y) for later on being able to create an RPC Server with this same user

Apply fixtures

.. code-block:: console

    make apply_fixtures

Run the server

.. code-block:: console

    make run


Add your admin user to the RPC group:

Now you should be able to navigate to http://localhost:8000/back/admin and log in with your previously created user.
