# Riddler Back

This project hold the [FSM](riddler/apps/fsm/lib/__init__.py) (Finite State Machine) and the Broker of the Riddler project, it can be considered the Back-end of riddler.

It also serves a very simple dummy [Front-end](riddler/back/riddler/apps/broker/templates/chat/index.html) just as an example of a WS connection to the backend from a custom widget.

## Installation

Three options to run this project: docker, local.

### 1. Docker Compose

As simple as running

`docker-compose up`

### 3. Set it up locally

Install machine requirements:

- Python 3.10
- python3.10-dev
- python3.10-distutils
- PostgreSQL
- gdal-bin
- poetry

Create a .env file with the needed variables set. You can see an example of those on [.env_example](.env_example)

This project is based on [Model-W](https://github.com/ModelW/project-maker) therefore we use poetry for the management of the dependencies

Go inside ./back directory Create and install project dependencies:

`poetry install`

Activate the virtual environment

`poetry shell`

Create a 'riddler' database in postgres

`sudo -u postgres psql -c "CREATE DATABASE riddler"`

Create a 'riddler' user in postgres

`sudo -u postgres psql -c "CREATE user riddler WITH encrypted password 'riddler';"`

Grant to the newly created user the proper the privileges to the database

`sudo -u postgres psql -c "grant all privileges on database riddler to riddler;"`

Apply django fixtures

`make apply_fixtures`

Create a superuser

`./manage.py createsuperuser`


Run the server

`make run`


## Quick Start

### Concepts

- <ins>Consumer</ins>: A broker is the layer responsible to connect the message platform (MP) (Telegram, WhatsApp, Signal, etc...) with the FSM and hold the session of a conversation. It knows hot to serialize the messages from the MP to the FSM and vice versa, and it knows how to send the resulting FSM's messages to the MP.


- <ins>FSM Definition</ins>: The FSM Definition is the description of the different states the bot exists on, and the transitions that describe how to pass from one state to the other.
<br/>This definition lives on Riddler's database but typically gets defined from the SDK.
<br/>We won't explain it further in this tutorial. If you wish a more detailed explanation go to the [SDK's README.md](../sdk/README.md)

### Example

This repository comes with examples of 2 different bots: a Telegram bot and a custom bot that connects with a WS client. We will be explaining both on this tutorial


#### Consumers

There are 2 types of consumers you can inherit from: HTTP based (HTTPBotConsumer) or WS based (WSBotConsumer)

Regardless of which one you inherit from, you need to implement the next attributes & methods:

- __serializer_class__: This class attribute should be a class that inherits from __BotMessageSerializer__ and implements:
  - to_mml: method that serialize the data coming from the platform to an MML message format
  - to_platform: method that serialize the MML from the FSM to a format the used platform undestands


- __gather_conversation_id__: Method that returns a unique identifier of a conversation/session. For HTTPBotConsumer this gets executed on every message, for WSBotConsumers only when the connection get established.


- __gather_fsm_def__: Method that returns the FSM definition that the connexion is going to use. For HTTPBotConsumer this gets executed on every message, for WSBotConsumers only when the connection get established.


- __platform_url_path__: It creates the URL that will be exposed by Django and to which the client is going to connect in order o talk with the consumer


- __register__: In case we need to notify the remote MP information as such a webhook. This method will be executed for all the BotConsumers when initializing the server.


- __send_response__: This method should be only implemented for those consumers that inherits from HTTPBotConsumer. The reason for it is because the response of a WS connection is usually the connection itself, on the other hand a bot that operates through HTTP usually does not include it response to the original request.


###### Telegram's consumer implementation

The full Telegram's consumer can be found under [here](riddler/apps/broker/consumers/bots/telegram.py)

Next we explain its different parts:

- _gather_conversation_id_: When telegram sends a user's message to our registered web-hook it includes within it will include the conversation's identifier under "message" -> "chat" -> "id"
```python
...
    def gather_conversation_id(self, validated_data):
        return validated_data["message"]["chat"]["id"]
...
```

- _gather_fsm_def_: For this specific bot we will keep it simple and select the first FSm on the DB. We could have implemented a sophisticated way of selecting FSM from the bot conversation interpreting LSD commands coming from the user but that will go outside scope of this example.
```python
...
    async def gather_fsm_def(self, validated_data):
        return await sync_to_async(FSMDefinition.objects.first)()
...
```
- _platform_url_path_: The URL that Django is going to expose so Telegram can send us the users messages to the bot, we include Telegram's token on the URL for security reasons.
```python
...
    @classmethod
    def platform_url_path(self) -> str:
        return f"back/webhooks/broker/telegram/{self.TOKEN}"
...
```
- _register_: As mentioned in the previous method, Telegram needs to know the web-hook URL to which it has to send the user's messages. Here in the `register` function we notify to the Telegram API which one is our web-hook, `register` get executed when the server starts.
```python
...
    @classmethod
    def register(cls):
        webhookUrl = urljoin(settings.BASE_URL, cls.platform_url_path())
        logger.debug(f"Notifying to Telegram our WebHook Url: {webhookUrl}")
        res = requests.get(
            f"{cls.API_URL}{cls.TOKEN}/setWebhook",
            params={"url": webhookUrl},
        )
        if res.ok:
            logger.debug(
                f"Successfully notified  WebhookUrl ({webhookUrl}) to Telegram"
            )
        else:
            logger.error(
                f"Error notifying  WebhookUrl ({webhookUrl}) to Telegram: {res.text}"
            )
...
```
- _send_response_: As mentioned earlier, since this bot is based on HTTPBotConsumer, how we send the messages coming from the FSM has to be defined under `send_response`. As you can see we will send the data to the Telgram's API endpoint: _/sendMessage_. Which data? you would ask, well: the MML comming from the FSM that passed to our `serialized_class` can be converted into Telegram API payload
```python
...
    async def send_response(self, mml: Message):
        async with httpx.AsyncClient() as client:
            for data in self.serializer_class.to_platform(mml, self):
                await client.post(
                    f"{self.API_URL}{self.TOKEN}/sendMessage", data=data
                )
...
```
- _serializer_class_: We set our class for serializing Telegram to FSM and vice versa to be TelegramMessageSerializer.
```python
...
    serializer_class = TelegramMessageSerializer
...
```
Let's look into this class better:
###### Telegram's serializer

The `serialize_class` from any consumer has to inherit from `BotMessageSerializer` which is a child of the DRF's Serialize class

First of all you should define your serializer as any other DRF serializer. It fields should represent the incoming messages from the MP, in this case Telegram.
```python
class TelegramMessageSerializer(BotMessageSerializer):
    message = TelegramPayloadSerializer()
...
```
- _to_mml_: This method should create an MML message from the message coming from the MP. It will most likely feed the `MessageSerializer` with the `validated_data` of itself, save it and return the resulting MML instance
```python
...
    def to_mml(self, ctx: BotConsumer) -> Union[bool, "Message"]:

        if not self.is_valid():
            return False
        last_mml = async_to_sync(ctx.get_last_mml)()
        s = MessageSerializer(
            data={
                "stacks": [[{"type": "text", "payload": self.validated_data["message"]["text"]}]],
                "transmitter": {
                    "first_name": self.validated_data["message"]["from"]["first_name"],
                    "type": AgentType.human.value,
                    "platform": "Telegram",
                },
                "send_time": self.validated_data["message"]["date"] * 1000,
                "conversation": self.validated_data["message"]["chat"]["id"],
                "prev": last_mml.pk if last_mml else None
            }
        )
        if not s.is_valid():
            return False
        return s.save()
...
```
- _to_platform_: Here we transform the stack of messages coming from an FSM's answer to something that Telegram would understand. Telegram supports very rich type of messages, again, this will go out of the scope of the example, so we will keep it siple and send simple single text message to Telegram.
```python
...
    @staticmethod
    def to_platform(mml: "Message", ctx: BotConsumer):
        for stack in mml.stacks:
            for layer in stack:
                if layer.get("type") == "text":
                    data = {
                        "chat_id": ctx.conversation_id,
                        "text": layer["payload"],
                        "parse_mode": "Markdown",
                    }
                    yield data
                else:
                    logger.warning(f"Layer not supported: {layer}")
...
```

The only thing left is to expose our server and configure our Telegram's token

First, obtain a Telegram token from a bot and add it in your .env
```
TG_TOKEN=<YOUT_TG_TOKEN>
```

This setting will be picked up by `TelegramBotConsumer`

```python
TOKEN = settings.TG_TOKEN
```

Then run your service under https using, for example, ngrok `ngrok http 8000`.

Then run docker-compose:

`BASE_URL=<HTTPS_ADDRESS> docker-compose up`

Or if you are running it straight in you machine make sure to include in your .env

`BASE_URL=<HTTPS_ADDRESS>`

###### Custom's consumer implementation

The full Custom WS's consumer can be found under [here](riddler/apps/broker/consumers/bots/custom_ws.py)

Next we explain its different parts:

- _gather_conversation_id_: The conversation identifier comes as a URL param. When the client connect to our Web Socket then part of the URL contains this ID
```python
...
    def gather_conversation_id(self):
        return self.scope["url_route"]["kwargs"]["conversation"]
...
```

- _gather_fsm_def_: Same as the conversation identifier, the FSM definiton identifier comes as a URL param when the client connects with the WS.
```python
...
    async def gather_fsm_def(self):
        pk = self.scope["url_route"]["kwargs"]["fsm_def_id"]
        return await sync_to_async(FSMDefinition.objects.get)(pk=pk)
...
```
- _platform_url_path_: The URL of our custom bot will contain the information of the conversation's ID and the FSM definition's ID for, later on, being picked up in `gather_conversation_id` and `gather_fsm_def` as already mentioned
```python
...
    @classmethod
    def platform_url_path(self) -> str:
        return r"back/ws/broker/(?P<conversation>\w+)/(?P<fsm_def_id>\w+)/$"
...
```
- _register_: We need to do nothing here since our custom bot is intended to be used directly, meaning we are going to connect to the resulting `platform_url_path` straight from the client (via WS)
```python
...
    @classmethod
    def register(cls):
        pass
...
```
- _serializer_class_: We set our class for serializing our custom client to FSM and vice versa to be ExampleWSSerializer.
```python
...
    serializer_class = ExampleWSSerializer
...
```
Let's look into this class better:

###### Custom WS's serializer

Our custom client will send a list of stack of messages with the same format as MML expects

```python
class ExampleWSSerializer(BotMessageSerializer):
    stacks = serializers.ListField(child=serializers.ListField(child=MessageStackSerializer()))
...
```
- _to_mml_: For creating the final MML we just have to add some extra properties as `transmitter`, `send_time`, `conversation` and `prev`. The stacks we use them as they come after validation.
```python
...
    def to_mml(self, ctx: BotConsumer) -> Union[bool, "Message"]:

        if not self.is_valid():
            return False

        last_mml = async_to_sync(ctx.get_last_mml)()
        s = MessageSerializer(
            data={
                "stacks": self.data["stacks"],
                "transmitter": {
                    "type": AgentType.human.value,
                    "platform": "WS",
                },
                "send_time": int(time.time() * 1000),
                "conversation": ctx.conversation_id,
                "prev": last_mml.pk if last_mml else None
            }
        )
        if not s.is_valid():
            return False
        return s.save()
...
```
- _to_platform_: We do not have to modify the message coming from the FSM since our client knows how to read MML messages, although for the moment only supports type text messages.
```python
...
    @staticmethod
    def to_platform(mml: "Message", ctx: BotConsumer) -> dict:
        for stack in mml.stacks:
            for layer in stack:
                if layer.get("type") == "text":
                    data = {
                        "status": WSStatusCodes.ok.value,
                        "payload": layer["payload"]
                    }
                    yield data
                else:
                    logger.warning(f"Layer not supported: {layer}")
...
```


## Endpoints

Custom WS chat: http://localhost:8000/back/api/broker/chat/

Admin: http://localhost:8000/back/admin/

Swagger Docs: http://localhost:8000/back/api/schema/swagger-ui/

Redoc Docs: http://localhost:8000/back/api/schema/redoc/


## Build the docs

go inside the `doc` directory and run:

```
poetry run make html
```
