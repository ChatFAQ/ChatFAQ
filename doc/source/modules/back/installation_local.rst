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

Create a 'riddler' database in postgres

.. code-block:: console

    sudo -u postgres psql -c "CREATE DATABASE riddler"

Create a 'riddler' user in postgres

.. code-block:: console

    sudo -u postgres psql -c "CREATE user riddler WITH encrypted password 'riddler';"

Grant to the newly created user the proper the privileges to the database

.. code-block:: console

    sudo -u postgres psql -c "grant all privileges on database riddler to riddler;"

Apply django migrations

.. code-block:: console

    ./manage.py migrate

Create a superuser

.. code-block:: console

    ./manage.py createsuperuser

Run the server

.. code-block:: console

    make run
