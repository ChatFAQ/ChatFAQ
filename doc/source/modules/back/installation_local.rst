Local Installation
==================

.. module:: back

Create a .env file with the needed variables set. You can see an example of those on :ref:`env_example`

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

Apply fixtures

.. code-block:: console

    make apply_fixtures

Run the server

.. code-block:: console

    make run
