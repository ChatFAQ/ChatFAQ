.. ChatFAQ documentation master file, created by
   sphinx-quickstart on Tue Feb  7 11:59:37 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

ChatFAQ's documentation
===================================


ChatFAQ is a comprehensive ecosystem for building chatbots, including generic chatbots, chatbots that learn from business-specific data, chatbots that redirect user requests to human operators, and any other type of chatbot you can imagine.

The system is comprised of three main components:

- The Back-end, also known as "Riddler," manages client-to-message platform connections and session storage. It also houses the database storing all Finite State Machine (FSM) definitions, user information, and more.

    :ref:`Riddler docs <Riddler's documentation>`

- The SDK serves two primary functions: it allows for the posting of new FSM definitions to Riddler, and it also launches an Remote Procedure Call (RPC) server to execute transitions and events from the posted FSM definitions.

    :ref:`SDK docs <SDK's documentation>`

- The Message Platform (MP) is the client application where the user interacts with the bot. Examples of MP include platforms such as WhatsApp, Telegram, Facebook Messenger, or a custom interface.

    :ref:`Widget docs <Widget's documentation>`

.. image:: ./_static/images/chatfaq_components.png


Contents
--------------------------

.. toctree::
   :maxdepth: 2

   ChatFAQ docs <index.rst>
   Riddler docs <modules/back/index.rst>
   SDK docs <modules/sdk/index.rst>
   Widget docs <modules/widget/index.rst>
