# Widget documentation

We built for you a custom front-end solution just so you can talk with your chatbot from the browser using an app you own. Although you can also connect any other message platform as such WhatsApp, Telegram, Signal, Facebook messenger, etc... ChatFAQ supports them all and if it doesn't it can easily be extended to do so.

## Usage

### JS Library

```html
<div id="chatfaq-widget"></div>

<script>
    import { ChatfaqWidget } from "chatfaq-widget";

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
    import { ChatfaqWidgetCustomElement } from "chatfaq-widget";
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

`manageUserId`: In case you want to keep track of the user's conversations, you can set this parameter to true and the widget will generate a random id for you and store it as a cookie so it can be sent to the backend on each request. Later on the widget will be able to retrieve the conversations history of the user.

`userId`: In case you rather use your own user id, you can set this parameter to the id you want, keep in mind that you will need to set the `manageUserId` parameter to false.

`fsmDef`: name of the FSM definition to use.

`title`: title which will appear on the header of the chatbot

`subtitle`: subtitle which will appear on the footer of the chatbot

`historyOpenedDesktop`: whether the widget starts with the left menu opened on desktop.

`historyOpenedMobile`: whether the widget starts with the left menu opened on mobiles.

`maximized`: if the widget starts maximized.

### Widget styles

We made the widget styles hightly customizable by exposing a set of variables that controls greatly the look and feel if it. You can easely overwrite them as shown in the next example:

```html

<script type="text/javascript" src="chatfaq-widget"></script>
<style>
    :root {
        --chatfaq-color-primary-200: red;
        --chatfaq-color-secondary-pink-500: blue;
        --chatfaq-color-tertiary-blue-500: green;
        --chatfaq-color-tertiary-green-500: black;
    }
</style>
```

You can find the full list of variables on [widget/assets/styles/_variables.css](../../../../widget/assets/styles/_variables.css)
