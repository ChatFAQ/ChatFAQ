.. riddler documentation master file, created by
   sphinx-quickstart on Mon Jan 16 12:29:01 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Riddler's documentation!
===================================

This project hold the :ref:`fsm` (Finite State Machine) and the Broker of the Riddler project, it can be considered the Back-end of riddler.

It also serves a very simple dummy [Front-end](riddler/back/riddler/apps/broker/templates/chat/index.html) just as an example of a WS connection to the backend from a custom widget.

Prerequisites
#############

You could either run this project from Docker or install it locally. Depending on your choice you will need different prerequisites.

- :ref:`Docker Prerequisites`
- :ref:`Local Prerequisites`


Installation
############

As mentioned before, run this project from Docker or install it locally.

- :ref:`Docker Installation`
- :ref:`Local Installation`

FSM
###

Explained on the `SDK <SDK>`_ documentation

Platform Configurations
#######################

First step when creating a new bot is configuring how we are going to connect with the message platform (MP).

You do so by creating a new record in the database from the `admin <https://localhost:8000/back/admin/broker/platformconfig/3/change/>`_ site.

There you assign the configuration to an existing FSM, add a type and meta information that later you might need as such tokens from the messenger platform or other data

Then if you implemented a new platform type you will have to inheriting from :ref:`PlatformConfig` and implementing its next 4 methods:

* :obj:`get_queryset <riddler.apps.broker.models.platform_config.PlatformConfig.get_queryset>`: It should filter the set of these platforms excluding any other platform, most likely by filtering by its platform_type
    ::
* :obj:`platform_url_path <riddler.apps.broker.models.platform_config.PlatformConfig.platform_url_path>`: For controlling the view's url depending on the platform type since this name will most likely depend on the metadata of the platform
    ::
* :obj:`platform_consumer <riddler.apps.broker.models.platform_config.PlatformConfig.platform_consumer>`: The HTTP/WS consumer AKA broker associated with the config, we will discuss brokers in the next section
    ::
* :obj:`register <riddler.apps.broker.models.platform_config.PlatformConfig.register>`: In case we need to notify the remote MP information as such our endpoint. This method will be executed for all platform configs when initializing the app

You can see 2 examples of Platform configurations in: :ref:`TelegramPlatformConfig` and :ref:`CustomWSPlatformConfig`


Brokers
#######

A broker is the layer responsible to make the message platform (MP) and the FSM understand each other. It has 2 responsibilities

* Serialize the messages from the MP to the FSM and vice versa

* Sending it

You should inherit one out of the 2 abstract classes provided:

* :obj:`HTTPBotConsumer <riddler.apps.broker.consumers.bot_examples.telegram>`: In case you communicate with your MP through HTTP.

    You can find an example of a Telegram bot based on HTTP using this interface here: :ref:`TelegramBotConsumer`

* :obj:`WSBotConsumer <riddler.apps.broker.consumers.bot_examples.custom_ws>`: In case you communicate with your MP through WS.

    You can find an example of a custom bot based on WS using this interface here: :ref:`CustomWSBotConsumer`


And implement the next 3 things:

* :obj:`gather_platform_config <riddler.common.abs.bot_consumers.BotConsumer.gather_platform_config>`: a method to collect the platform config once a connection is stablished with the consumer
    ::
* :obj:`gather_conversation_id <riddler.common.abs.bot_consumers.BotConsumer.gather_conversation_id>`: a method to determine the conversation identifier once a connection is stablished with the consumer
    ::
* :obj:`serializer_class <riddler.common.abs.bot_consumers.BotConsumer.serializer_class>` The serialization from the MP to the MML and from the FSM to the MP is done by creating a new serializer which inherits from :ref:`BotMessageSerializer` and settings its serializer_class to it,
    ::

from this serializer you should implement :obj:`to_mml <riddler.apps.broker.serializers.message.BotMessageSerializer.to_mml>` and :obj:`to_platform <riddler.apps.broker.serializers.message.BotMessageSerializer.to_platform>` methods

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. toctree::
   :hidden:
   :caption: Contents:

   modules/prerequisites_docker.rst
   modules/prerequisites_local.rst
   modules/installation_docker.rst
   modules/installation_local.rst
   modules/platform_config.rst
   modules/telegram_platform_config.rst
   modules/custom_ws_platform_config.rst
   modules/bot_consumer.rst
   modules/http_bot_consumer.rst
   modules/ws_bot_consumer.rst
   modules/telegram_bot_consumer.rst
   modules/custom_ws_bot_consumer.rst
   modules/bot_message_serializer.rst
   modules/env_example.rst
   modules/fsm.rst
