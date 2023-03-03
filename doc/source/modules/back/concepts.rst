
Concepts
==================

If your intention is to connect our custom :ref:`widget <Widget's documentation>` to your already installed ChatFAQ back-end server, then no further information is necessary.

However, if you desire to create a new consumer to connect to a different type of messaging platform, please continue reading.


.. role:: underline

- :underline:`Consumer`: A broker is the layer responsible for connecting the messaging platform (MP) (Telegram, WhatsApp, Signal, etc.) with the FSM and holding the session of a conversation. It knows how to serialize the messages from the MP to the FSM and vice versa, and it knows how to send the resulting FSM's messages to the MP.


- :underline:`FSM Definition`: The FSM Definition is the description of the different states the bot exists in, and the transitions that describe how to pass from one state to the other.

The definition is stored in ChatFAQ back-end database but is typically defined via the SDK.


We won't explain it further in this tutorial. If you wish a more detailed explanation, go to the [SDK's README.md](../sdk/README.md)

Example
------------------

This repository comes with examples of 2 different bots: a Telegram bot and a custom bot that connects with a WS client. We will be explaining both in this tutorial.


Consumers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are 2 types of consumers you can inherit from: HTTP based (HTTPBotConsumer) or WS-based (WSBotConsumer).

Regardless of which one you inherit from, you need to implement the following attributes and methods:

- **serializer_class**: This class attribute should be a class that inherits from **BotMessageSerializer** and implements:
  - to_mml: method for serializing data from the messaging platform into MML message format
  - to_platform: method for serializing MML from the FSM to a format that the messaging platform supports


- **gather_conversation_id**: A method that returns a unique identifier of a conversation or session. For HTTPBotConsumer, this gets executed on every message; for WSBotConsumers, only when the connection is established.


- **gather_fsm_def**: Method that returns the FSM definition that the connection is going to use. For HTTPBotConsumer, this gets executed on every message; for WSBotConsumers, only when the connection is established.


- **platform_url_path**: It creates the URL that will be exposed by Django and to which the client is going to connect in order to talk with the consumer.


- **register**: If we need to notify the remote MP information using a webhook, we can do so. This method will be executed for all the bot consumers when initializing the server.


- **send_response**: This method should be only implemented for those consumers that inherit from HTTPBotConsumer. The reason for it is because the response of a WS connection is usually the connection itself; on the other hand, a bot that operates through HTTP usually does not include its response to the original request.


Telegram's consumer implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The full Telegram's consumer can be found :ref:`here <telegram_bot>`

Next, we explain its different parts:

- *gather_conversation_id*: When Telegram sends a user's message to our registered web-hook, it includes within it the conversation's identifier under "message" -> "chat" -> "id"

.. literalinclude:: ../../../../back/back/apps/broker/consumers/bots/telegram.py
   :language: python
   :lines: 22-23

- *gather_fsm_def*: For this specific bot, we will keep it simple and select the first FSM on the DB. We could have implemented a sophisticated way of selecting FSM from the bot conversation by interpreting LSD commands coming from the user, but that will go outside the scope of this example.

.. literalinclude:: ../../../../back/back/apps/broker/consumers/bots/telegram.py
   :language: python
   :lines: 25-26

- *platform_url_path*: The URL that Django is going to expose so Telegram can send us the users' messages to the bot, and we include Telegram's token on the URL for security reasons.

.. literalinclude:: ../../../../back/back/apps/broker/consumers/bots/telegram.py
   :language: python
   :lines: 28-30

- *register*: As mentioned in the previous method, Telegram needs to know the web-hook URL to which it has to send the user's messages. In the `register` function, we notify to the Telegram API, which serves as our web-hook, that the `register` will be executed when the server boots up.

.. literalinclude:: ../../../../back/back/apps/broker/consumers/bots/telegram.py
   :language: python
   :lines: 32-47

- *send_response*: As mentioned earlier, since this bot is based on HTTPBotConsumer, how we send the messages coming from the FSM has to be defined under `send_response`. As you can see, we will send the data to Telgram's API endpoint: **sendMessage_. Which data? You might be wondering how the MML from the FSM that was passed to our `serialized_class` can be converted into Telegram API payload

.. literalinclude:: ../../../../back/back/apps/broker/consumers/bots/telegram.py
   :language: python
   :lines: 49-54

- *serializer_class*: We set our class for serializing Telegram to FSM and vice versa to be TelegramMessageSerializer.

.. literalinclude:: ../../../../back/back/apps/broker/consumers/bots/telegram.py
   :language: python
   :lines: 18

Let's look into this class better:

Telegram's serializer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The full Telegram's serializer can be found :ref:`here <telegram_serializer>`

The *serialize_class* from any consumer has to inherit from *BotMessageSerializer*, which is a child of the DRF's Serialize class

To begin, define your serializer as any other DRF serializer. Its fields should represent the incoming messages from the MP, in this case, Telegram.

.. literalinclude:: ../../../../back/back/apps/broker/serializers/messages/telegram.py
   :language: python
   :lines: 49-50

- *to_mml*: This method should create an MML message from the message coming from the MP. It will most likely feed a **MessageSerializer** with its own **validated_data**, save it, and return the resulting MML instance.

.. literalinclude:: ../../../../back/back/apps/broker/serializers/messages/telegram.py
   :language: python
   :lines: 52-72

- *to_platform*: Here we transform the stack of messages coming from an FSM's answer to something that Telegram would understand. Telegram supports very rich types of messages; again, this will go outside the scope of the example, so we will keep it simple and send a simple single text message to Telegram.

.. literalinclude:: ../../../../back/back/apps/broker/serializers/messages/telegram.py
   :language: python
   :lines: 74-86


The only thing left is to expose our server and configure Telegram's token.

First, obtain a Telegram token from a bot and add it to your .env

::

    TG_TOKEN=<YOUT_TG_TOKEN>

This setting will be picked up by **TelegramBotConsumer**

::

    TOKEN = settings.TG_TOKEN

Then run your service under https using, for example, ngrok :code:`ngrok http 8000`.

Then run docker-compose:

:code:`BASE_URL=<HTTPS_ADDRESS> docker-compose up`

If you are running it directly in your machine, include it in your .env

::

    BASE_URL=<HTTPS_ADDRESS>

Custom WS consumer implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The complete Custom WS's consumer can be found here :ref:`here <custom_ws_bot>`

Next, we explain its different parts:

- *gather_conversation_id*: The conversation identifier comes as a URL param. When the client connects to our Web Socket then part of the URL contains this ID.

.. literalinclude:: ../../../../back/back/apps/broker/consumers/bots/custom_ws.py
   :language: python
   :lines: 19-20

- *gather_fsm_def*: Same as the conversation identifier, the FSM definition identifier comes as a URL param when the client connects with the WS.

.. literalinclude:: ../../../../back/back/apps/broker/consumers/bots/custom_ws.py
   :language: python
   :lines: 22-24

- *platform_url_path*: The URL of our custom bot will contain the conversation ID and the FSM definition ID, which will be picked up later in `gather_conversation_id` and `gather_fsm_def` as previously mentioned.

.. literalinclude:: ../../../../back/back/apps/broker/consumers/bots/custom_ws.py
   :language: python
   :lines: 26-28

- *register*: We need to do nothing here since our custom bot is intended to be used directly, meaning we are going to connect to the resulting `platform_url_path` straight from the client (via WS).

.. literalinclude:: ../../../../back/back/apps/broker/consumers/bots/custom_ws.py
   :language: python
   :lines: 30-32

- *serializer_class*: We set our class for serializing our custom client to FSM and vice versa to be ExampleWSSerializer.

.. literalinclude:: ../../../../back/back/apps/broker/consumers/bots/custom_ws.py
   :language: python
   :lines: 17

Let's look into this class better:

Custom WS serializer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The full Custom WS serializer can be found under :ref:`here <telegram_serializer>`

Our custom client will send a list of stacked messages with the same format as MML expects.

.. literalinclude:: ../../../../back/back/apps/broker/serializers/messages/custom_ws.py
   :language: python
   :lines: 23-24

- *to_mml*: For creating the final MML, we just have to add some extra properties as `transmitter`, `send_time`, `conversation` and `prev`. The stacks we use them as they come after validation.

.. literalinclude:: ../../../../back/back/apps/broker/serializers/messages/custom_ws.py
   :language: python
   :lines: 26-46

- *to_platform*: We do not have to modify the message coming from the FSM since our client knows how to read MML messages, although for the moment only supports type text messages.

.. literalinclude:: ../../../../back/back/apps/broker/serializers/messages/custom_ws.py
   :language: python
   :lines: 49-59

