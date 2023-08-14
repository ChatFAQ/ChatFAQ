# ChatFAQ's Widget

We built for you a custom front-end solution just so you can talk with your chatbot from the browser using an app you own. Although you can also connect any other message platform as such WhatsApp, Telegram, Signal, Facebook messenger, etc... ChatFAQ supports them all and if it doesn't it can easily be extended to do so.

## Prerequisites

Make sure the next list of packages are installed on your system:

- npm
- node v19.6.0


## Installation

### NPM

    npm install chatfaq-widget

### UNPKG

    <script src="unpkg.com/chatfaq-widget/dist/widget-loader.min.esm"></script>

### Local build

#### Set Up:

Install project dependencies:

    npm i

## Run

First of all, create a `.env` file with the needed variables set. You can see an example of those on [.env_example](.env_example) file. Next you can see the explanation of each variable:

`CHATFAQ_BACKEND_API`: The address for the HTTP of the back-end server.

`CHATFAQ_BACKEND_WS`:  The address for the WS of the back-end server.

Run the example:

    npm run dev

This will run a node server which will serve an empty webpage with just the Widget integrated on it, if you navigate to http://localhost:3000

## Usage

### JS Library

```html
<div id="chatfaq-widget"></div>

<script>
    import { ChatfaqWidget } from "chatfaq-widget/dist/widget-loader.esm";

    const config = {
        element: "#chatfaq-widget",
        chatfaqApi: "http://127.0.0.1:8000",
        chatfaqWs: "ws://127.0.0.1:8000",
        userId: 1234567890,
        fsmDef: "simple_fsm",
        title: "Hello there 👋",
        subtitle: "How can we help you?",
        historyOpened: true,
        maximized: false
    }

    const chatfaqWidget = new ChatfaqWidget(config);

</script>
```

It is also possible to pass the config keys as data attributes to the mounted element as such:

```html
<div
    id="chatfaq-widget"
    data-chatfaq-api="http://127.0.0.1:8000"
    data-chatfaq-ws="ws://127.0.0.1:8000"
    user-id="1234567890"
    data-fsm-def="simple_fsm"
    data-title="Hello there 👋"
    data-subtitle="How can we help you?"
    history-opened="true"
    maximized="false"
></div>
```
If you declare data attributes and a config object and its keys collide, then the config object will have priority.

### Web-Component

```html

<script>
    import { ChatfaqWidgetCustomElement } from "chatfaq-widget/dist/widget-loader.esm";
    customElements.define("chatfaq-widget", ChatfaqWidgetCustomElement)
</script>

<chatfaq-widget
    data-chatfaq-api="http://127.0.0.1:8000"
    data-chatfaq-ws="ws://127.0.0.1:8000"
    data-user-id="1234567890"
    data-fsm-def="simple_fsm"
    data-title="Hello there 👋"
    data-subtitle="How can we help you?"
    data-history-opened="true"
    data-maximized="false"
></chatfaq-widget>
```

### Widget params

Next we will explain all the widget's possible parameters:

`element`: string selector or HTMLElement to which the widget will be attached.

`chatfaqApi`: url of the chatfaq-api.

`chatfaqWs`: url of the chatfaq-ws.

`userId`: In case you want to keep track of the user's conversations, you can pass a userId to the widget. This id will be store as a cookie and will be sent to the backend on each request. Later on the widget will be able to retrieve the conversations history of the user.

`fsmDef`: name of the FSM definition to use.

`title`: title which will appear on the header of the chatbot

`subtitle`: subtitle which will appear on the footer of the chatbot

`historyOpened`: if the widget starts with the left menu opened.

`maximized`: if the widget starts maximized.

### Widget styles

We made the widget styles hightly customizable by exposing a set of variables that controls greatly the look and feel if it. You can easely overwrite them as shown in the next example:

```html

<script type="text/javascript" src="chatfaq-widget/dist/widget-loader.esm"></script>
<style>
    :root {
        --chatfaq-color-primary-200: red;
        --chatfaq-color-secondary-pink-500: blue;
        --chatfaq-color-tertiary-blue-500: green;
        --chatfaq-color-tertiary-green-500: black;
    }
</style>
```

You can find the full list of variables on [assets/styles/_variables.css](assets/styles/_variables.css)
