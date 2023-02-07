
Quick Start
==================

Concepts
------------------

.. role:: underline

- :underline:`Consumer`: A broker is the layer responsible to connect the message platform (MP) (Telegram, WhatsApp, Signal, etc...) with the FSM and hold the session of a conversation. It knows hot to serialize the messages from the MP to the FSM and vice versa, and it knows how to send the resulting FSM's messages to the MP.


- :underline:`FSM Definition`: The FSM Definition is the description of the different states the bot exists on, and the transitions that describe how to pass from one state to the other.

This definition lives on Riddler's database but typically gets defined from the SDK.


We won't explain it further in this tutorial. If you wish a more detailed explanation go to the [SDK's README.md](../sdk/README.md)

Example
------------------

This repository comes with examples of 2 different bots: a Telegram bot and a custom bot that connects with a WS client. We will be explaining both on this tutorial


Consumers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are 2 types of consumers you can inherit from: HTTP based (HTTPBotConsumer) or WS based (WSBotConsumer)

Regardless of which one you inherit from, you need to implement the next attributes & methods:

- **serializer_class**: This class attribute should be a class that inherits from **BotMessageSerializer** and implements:
  - to_mml: method that serialize the data coming from the platform to an MML message format
  - to_platform: method that serialize the MML from the FSM to a format the used platform undestands


- **gather_conversation_id**: Method that returns a unique identifier of a conversation/session. For HTTPBotConsumer this gets executed on every message, for WSBotConsumers only when the connection get established.


- **gather_fsm_def**: Method that returns the FSM definition that the connexion is going to use. For HTTPBotConsumer this gets executed on every message, for WSBotConsumers only when the connection get established.


- **platform_url_path**: It creates the URL that will be exposed by Django and to which the client is going to connect in order o talk with the consumer


- **register**: In case we need to notify the remote MP information as such a webhook. This method will be executed for all the BotConsumers when initializing the server.


- **send_response**: This method should be only implemented for those consumers that inherits from HTTPBotConsumer. The reason for it is because the response of a WS connection is usually the connection itself, on the other hand a bot that operates through HTTP usually does not include it response to the original request.


Telegram's consumer implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The full Telegram's consumer can be found under :ref:`here <telegram_bot>`

Next we explain its different parts:

- *gather_conversation_id*: When telegram sends a user's message to our registered web-hook it includes within it will include the conversation's identifier under "message" -> "chat" -> "id"

.. literalinclude:: ../../../../back/riddler/apps/broker/consumers/bots/telegram.py
   :language: python
   :lines: 22-23

- *gather_fsm_def*: For this specific bot we will keep it simple and select the first FSm on the DB. We could have implemented a sophisticated way of selecting FSM from the bot conversation interpreting LSD commands coming from the user but that will go outside scope of this example.

.. literalinclude:: ../../../../back/riddler/apps/broker/consumers/bots/telegram.py
   :language: python
   :lines: 25-26

- *platform_url_path*: The URL that Django is going to expose so Telegram can send us the users messages to the bot, we include Telegram's token on the URL for security reasons.

.. literalinclude:: ../../../../back/riddler/apps/broker/consumers/bots/telegram.py
   :language: python
   :lines: 28-30

- *register*: As mentioned in the previous method, Telegram needs to know the web-hook URL to which it has to send the user's messages. Here in the `register` function we notify to the Telegram API which one is our web-hook, `register` get executed when the server starts.

.. literalinclude:: ../../../../back/riddler/apps/broker/consumers/bots/telegram.py
   :language: python
   :lines: 32-47

- *send_response*: As mentioned earlier, since this bot is based on HTTPBotConsumer, how we send the messages coming from the FSM has to be defined under `send_response`. As you can see we will send the data to the Telgram's API endpoint: **sendMessage_. Which data? you would ask, well: the MML comming from the FSM that passed to our `serialized_class` can be converted into Telegram API payload

.. literalinclude:: ../../../../back/riddler/apps/broker/consumers/bots/telegram.py
   :language: python
   :lines: 49-54

- *serializer_class*: We set our class for serializing Telegram to FSM and vice versa to be TelegramMessageSerializer.

.. literalinclude:: ../../../../back/riddler/apps/broker/consumers/bots/telegram.py
   :language: python
   :lines: 18

Let's look into this class better:

Telegram's serializer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The full Telegram's serializer can be found under :ref:`here <telegram_serializer>`

The *serialize_class* from any consumer has to inherit from *BotMessageSerializer* which is a child of the DRF's Serialize class

First of all you should define your serializer as any other DRF serializer. It fields should represent the incoming messages from the MP, in this case Telegram.

.. literalinclude:: ../../../../back/riddler/apps/broker/serializers/messages/telegram.py
   :language: python
   :lines: 49-50

- *to_mml*: This method should create an MML message from the message coming from the MP. It will most likely feed the **MessageSerializer** with the **validated_data** of itself, save it and return the resulting MML instance

.. literalinclude:: ../../../../back/riddler/apps/broker/serializers/messages/telegram.py
   :language: python
   :lines: 52-72

- *to_platform*: Here we transform the stack of messages coming from an FSM's answer to something that Telegram would understand. Telegram supports very rich type of messages, again, this will go out of the scope of the example, so we will keep it siple and send simple single text message to Telegram.

.. literalinclude:: ../../../../back/riddler/apps/broker/serializers/messages/telegram.py
   :language: python
   :lines: 74-86


The only thing left is to expose our server and configure our Telegram's token

First, obtain a Telegram token from a bot and add it in your .env

::

    TG_TOKEN=<YOUT_TG_TOKEN>

This setting will be picked up by **TelegramBotConsumer**

::

    TOKEN = settings.TG_TOKEN

Then run your service under https using, for example, ngrok :code:`ngrok http 8000`.

Then run docker-compose:

:code:`BASE_URL=<HTTPS_ADDRESS> docker-compose up`

Or if you are running it straight in you machine make sure to include in your .env

::

    BASE_URL=<HTTPS_ADDRESS>

Custom WS consumer implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The full Custom WS's consumer can be found under :ref:`here <custom_ws_bot>`

Next we explain its different parts:

- *gather_conversation_id*: The conversation identifier comes as a URL param. When the client connect to our Web Socket then part of the URL contains this ID

.. literalinclude:: ../../../../back/riddler/apps/broker/consumers/bots/custom_ws.py
   :language: python
   :lines: 19-20

- *gather_fsm_def*: Same as the conversation identifier, the FSM definiton identifier comes as a URL param when the client connects with the WS.

.. literalinclude:: ../../../../back/riddler/apps/broker/consumers/bots/custom_ws.py
   :language: python
   :lines: 22-24

- *platform_url_path*: The URL of our custom bot will contain the information of the conversation's ID and the FSM definition's ID for, later on, being picked up in `gather_conversation_id` and `gather_fsm_def` as already mentioned

.. literalinclude:: ../../../../back/riddler/apps/broker/consumers/bots/custom_ws.py
   :language: python
   :lines: 26-28

- *register*: We need to do nothing here since our custom bot is intended to be used directly, meaning we are going to connect to the resulting `platform_url_path` straight from the client (via WS)

.. literalinclude:: ../../../../back/riddler/apps/broker/consumers/bots/custom_ws.py
   :language: python
   :lines: 30-32

- *serializer_class*: We set our class for serializing our custom client to FSM and vice versa to be ExampleWSSerializer.

.. literalinclude:: ../../../../back/riddler/apps/broker/consumers/bots/custom_ws.py
   :language: python
   :lines: 17

Let's look into this class better:

Custom WS serializer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The full Custom WS serializer can be found under :ref:`here <telegram_serializer>`

Our custom client will send a list of stack of messages with the same format as MML expects

.. literalinclude:: ../../../../back/riddler/apps/broker/serializers/messages/custom_ws.py
   :language: python
   :lines: 23-24

- *to_mml*: For creating the final MML we just have to add some extra properties as `transmitter`, `send_time`, `conversation` and `prev`. The stacks we use them as they come after validation.

.. literalinclude:: ../../../../back/riddler/apps/broker/serializers/messages/custom_ws.py
   :language: python
   :lines: 26-46

- *to_platform*: We do not have to modify the message coming from the FSM since our client knows how to read MML messages, although for the moment only supports type text messages.

.. literalinclude:: ../../../../back/riddler/apps/broker/serializers/messages/custom_ws.py
   :language: python
   :lines: 49-59

