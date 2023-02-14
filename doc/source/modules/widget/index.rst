Widget's documentation
=======================================

This is a simple implementation of a client chatbot that connect to a ChatFAQ's back-end server and offers a interface to communicate with a selected FSM

.. image:: ../../_static/images/chatfaq_components_mp.png

Prerequisite
---------------------

- node v19.5.0

Install
---------------------

Go inside *./widget* directory and install project dependencies:

.. code-block:: console

    npm i

Configuration
---------------------

Navigate inside :code:`./widget`

.. module:: widget

Create a :code:`.env` file with the needed variables set. You can see an example of those on the :ref:`.env_example <sdk_env_example>` file

.. literalinclude:: ../../../../widget/.env_example

Development Server
---------------------

Start the development server on http://localhost:3000

.. code-block:: console

    npm run dev

You are all set! Now you can navigate to http://localhost:3000 and test the widget!

Production
---------------------

Build the application for production:

.. code-block:: console

    npm run build

Locally preview production build:

.. code-block:: console

    npm run preview

Integration on external sites
-----------------------------

To integrate the chatbot interface into an external webpage, simply include the following script tag:

.. code-block:: html

    <script src="http://localhost:3000/js/IframeLoader.js"></script>
