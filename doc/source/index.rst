.. ChatFAQ documentation master file, created by
   sphinx-quickstart on Tue Feb  7 11:59:37 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to ChatFAQ's documentation!
===================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

ChatFAQ is a comprehensive ecosystem for building chatbots, including generic chatbots, chatbots that learn from business-specific data, chatbots that redirect user requests to human operators, and any other type of chatbot you can imagine.

The system is comprised of three main components:

- The Back-end, also known as "Riddler," manages client-to-message platform connections and session storage. It also houses the database storing all Finite State Machine (FSM) definitions, user information, and more.

:ref:`Riddler docs <Welcome to Riddler's documentation!>`

- The SDK serves two primary functions: it allows for the posting of new FSM definitions to Riddler, and it also launches an Remote Procedure Call (RPC) server to execute transitions and events from the posted FSM definitions.

- The Message Platform (MP) is the client application where the user interacts with the bot. Examples of MP include platforms such as WhatsApp, Telegram, Facebook Messenger, or a custom interface.

:ref:`SDK docs <Welcome to Riddler SDK's documentation!>`

.. image:: ._static/images/chatfaq_components.png


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
