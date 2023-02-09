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

Check out the [deployment documentation](https://nuxt.com/docs/getting-started/deployment) for more information.

Configuration
---------------------

.. module:: widget

Create a *.env* file with 2 variables: **RIDDLER_API** & **RIDDLER_WS** with its respective protocol + addreses . If you are developing locally you could just copy the content of :ref:`env_example`

Usage
---------------------

The idea is just to include a script tag pointing to this service in any external webpage that requires a chatbot interface.

So, in case you are developing locally:

.. code-block:: html

    <script src="http://localhost:3000/js/IframeLoader.js"></script>

should be enough.

Another option would be navigating to http://localhost:3000/ which will serve a blank page with the example script tag above appended to the body.
