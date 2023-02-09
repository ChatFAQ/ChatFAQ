Quick Start
==================

Development Server
---------------------

Start the development server on http://localhost:3000

.. code-block:: console

    npm run dev

Production
---------------------

Build the application for production:

.. code-block:: console

    npm run build

Locally preview production build:

.. code-block:: console

    npm run preview

Configuration
---------------------

.. module:: widget

Create a *.env* file and define two variables, **RIDDLER_API** and **RIDDLER_WS**, with their respective protocols and addresses. If you are developing locally, you can simply copy the contents of env_example.

Usage
---------------------

To integrate the chatbot interface into an external webpage, simply include the following script tag:

.. code-block:: html

    <script src="http://localhost:3000/js/IframeLoader.js"></script>

This assumes that you are developing locally. If not, please use the correct URL for the script.

Alternatively, you can navigate to http://localhost:3000/ to access a blank page that already has the example script tag appended to the body.
