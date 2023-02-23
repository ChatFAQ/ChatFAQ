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


Installation as an external dependency
-----------------------------

Node server

Via NPM

.. code-block:: console

    npm i chatfaq-widget

Or using UNPKG

.. code-block:: html

    <script src="unpkg.com/chatfaq-widget/dist/widget-loader.min.esm" ></script>


JS Library

.. code-block:: html

    <div id="chatfaq-widget" data-chatfaq-api="http://127.0.0.1:8008" data-chatfaq-ws="ws://127.0.0.1:8008"></div>

    <script>

        import { ChatfaqWidget } from "chatfaq-widget/dist/widget-loader.esm";

        const config = {
            element: "#chatfaq-widget",
            chatfaqApi: "http://127.0.0.1:8000",
            chatfaqWs: "ws://127.0.0.1:8000",
        };

        const chatfaqWidget = new ChatfaqWidget(config);

    </script>

Web-Component

.. code-block:: html

    import { ChatfaqWidgetCustomElement } from "chatfaq-widget/dist/widget-loader.esm";

    <script>

        customElements.define("chatfaq-widget", ChatfaqWidgetCustomElement)

    </script>

    <chatfaq-widget data-chatfaq-api="http://127.0.0.1:8000" data-chatfaq-ws="ws://127.0.0.1:8000"></chatfaq-widget>
