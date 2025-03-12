# Widget documentation

We built for you a custom front-end solution just so you can talk with your chatbot from the browser using an app you own. Although you can also connect any other message platform as such WhatsApp, Telegram, Signal, Facebook messenger, etc... ChatFAQ supports them all and if it doesn't it can easily be extended to do so.

## Prerequisites

Make sure the next list of packages are installed on your system:

- npm
- node v19.6.0


## Installation

### NPM

    npm install chatfaq-widget

### UNPKG

    <script src="unpkg.com/chatfaq-widget"></script>

### Local build

#### Set Up:

Install project dependencies:

    npm i

## Run

First of all, create a `.env` file with the needed variables set. You can see an example of those on [.env_example](.env_example) file. Next you can see the explanation of each variable:

`NUXT_PUBLIC_CHATFAQ_API`: The address for the HTTP of the back-end server.

`NUXT_PUBLIC_CHATFAQ_WS`:  The address for the WS of the back-end server.

Run the example:

    npm run dev

This will run a node server which will serve an empty webpage with just the Widget integrated on it, if you navigate to http://localhost:3000

## Usage


### Widget params

Next we will explain all the widget's possible parameters:

<span style="color:red;">*</span> → mandatory

<span style="color:orange;">*</span> → mandatory if not using an admin's widget configuration

`chatfaqApi`<span style="color:red;">*</span>: url of the chatfaq-api.

`element`<span style="color:red;">*</span> (only mandatory [with JS integration](#js-library)): string selector or HTMLElement to which the widget will be attached.

`chatfaqWs`<span style="color:orange;">*</span>: url of the chatfaq-ws.

`fsmDef`<span style="color:orange;">*</span>: name of the FSM definition to use.

`widgetConfigId` is the ID of the widget configuration to use. First, you need to create a widget configuration in the admin panel. If provided, the attributes explicitly defined on the element will override those in the admin's widget configuration, **except for boolean attributes**, which will be set to `true` if either the admin's widget configuration or the element's attributes have them set to `true`.

`conversationId`: id of the conversation to use, if not provided a new conversation will be created.

`userId`: All the conversations will be stored in the backend, so the widget needs to know which user they belong to, you have the option to provide your own userId or let the widget generate one for you.

`title`: title which will appear on the header of the chatbot

`subtitle`: subtitle which will appear on the footer of the chatbot

`lang` ('en'): language of the widget, we natively support 'en', 'es' and 'fr'.

`previewMode`: Preview mode is a special mode that allows you to see the widget with rendered mocked messages without the need of a backend server, this way you can see a preview on how the widget really looks like, it is useful for testing purposes.

`customCss`: custom css to be applied to the widget.

`hideSources`: if the sources should be hidden, by default the sources will be displayed.

`sourcesFirst`: It will reverse the default order of the sources and the chat, so the message's references will be displayed first.

`startWithHistoryClosed`: if the widget starts with the history closed, by default the widget has the history opened.

`startSmallMode`: if the widget starts in small mode, by default the widget starts in expanded mode.

`fullScreen`: if the widget should be in full screen mode, by default the widget is a bottom right window, this mode will make the widget take the whole screen.

`disableDayNightMode`: if the widget should disable the day/night mode, by default the widget has the day/night mode enabled.

`onlyChat`: if the widget should only display the chat, by default the widget displays the header and the history besides the chat.

`fitToParent`: if the widget should fit to the parent element, by default the widget will be positioned absolute to the window.

`stickInputPrompt`: if the input text should be sticked to the bottom of the chat, by default the input text will be sticked to the bottom of the chat but if for instance you choose to fit the widget to the parents height then the input text can disappear from the view.

`initialConversationMetadata`: stringify JSON object with arbitrary metadata that will be sent and accessible in the SDK's FSM

`customIFramedMsgs`: It is possible to customize the messages coming from the SDK's FSM, you can pass a JSON object with the following structure:

`speechRecognition`: It enables the speech recognition feature, by default it is disabled.

`speechRecognitionAutoSend`: If speech recognition should automatically send the recognized text once it detect the user stopped talking, by default it is disabled.

`allowAttachments`: If the widget should allow the user to send attachments, by default it is disabled.

`authToken`: The token to authenticate the user in case your FSM requires it.

`enableLogout`: If the widget should display a logout button, by default it is disabled. When the user clicks on the logout button an 'chatfaq-logout' event will be emitted from the document. You can listen to this event and handle the logout as you wish.

`enableResend`: If enabled, the widget will display a reset button on some messages that will allow the user to resend the message. This feature is under development and not fully implemented yet.

```json
{
    "<MESSAGE_TYPE>": {
        "src": "<URL>",
        "fullWidth": Boolean,
        "mobileNoMargins": Boolean,
        "desktopNoMargins": Boolean,
        "dynamicHeight": Boolean,
        "scrolling": "yes"/"no",
        "noPadding": Boolean
    }
}
```
The widget will intercept any message with the type `<MESSAGE_TYPE>` and will render an iframe with the provided URL. The rest of the parameters are optional and will be used to customize the iframe's styling and behavior, next you can see the explanation of each parameter:

- `src`<span style="color:red;">*</span>: URL of the iframe.
- `fullWidth`: If the iframe should take the full width of the chat's message in which it is contained.
- `mobileNoMargins`: If the message in which the iframe is contained should have no margins on mobile.
- `desktopNoMargins`: If the message in which the iframe is contained should have no margins on desktop.
- `dynamicHeight`: If the iframe should have a dynamic height, this will make the iframe's height to be the same as its content's height.
- `scrolling`: If the iframe should have scrolling, by default the iframe will have scrolling.
- `noPadding`: If the message in which the iframe is contained should have no padding, by default the message will have padding.


### JS Library

```html
<div id="chatfaq-widget"></div>

<script>
    import { ChatfaqWidget } from "chatfaq-widget";

    const config = {
        element: "#chatfaq-widget",
        chatfaqApi: "http://localhost:8000",
        chatfaqWs: "ws://localhost:8000",
        fsmDef: "simple_fsm",
        widgetConfigId: "1",
        conversationId: "1",
        userId: "1234567890",
        title: "Hello there 👋",
        subtitle: "How can we help you?",
        lang: "es",
        previewMode: true,
        customCss: ":root { --chatfaq-color-primary-200: red; }",
        hideSources: true,
        sourcesFirst: true,
        startWithHistoryClosed: true,
        startSmallMode: true,
        fullScreen: true,
        disableDayNightMode: true,
        onlyChat: true,
        fitToParent: true,
        stickInputPrompt: true,
        speechRecognition: true,
        speechRecognitionAutoSend: true,
        allowAttachments: true,
        initialConversationMetadata: JSON.stringify({"hello": "world"}),
        customIFramedMsgs: JSON.stringify({
            "iframe": {
                "src": "https://localhost:3000/iframed-msg",
                "fullWidth": true,
                "mobileNoMargins": true,
                "desktopNoMargins": true,
                "dynamicHeight": true,
                "scrolling": "np",
                "noPadding": true
            }
        }),
        authToken: "1234567890",
        enableLogout: true,
        enableResend: true
    }

    const chatfaqWidget = new ChatfaqWidget(config);

</script>
```

It is also possible to pass the config keys as data attributes (_data-element_, _data-chatfaq-api_, etc... ) to the element, the widget will read them and use them as the config object.

If you declare data attributes and a config object and its keys collide, then the config object will have priority.

### Web-Component

```html

<script>
    import { ChatfaqWidgetCustomElement } from "chatfaq-widget";
    customElements.define("chatfaq-widget", ChatfaqWidgetCustomElement)
</script>

<chatfaq-widget
    id="chatfaq-widget"
    data-chatfaq-api="http://127.0.0.1:8000"
    data-chatfaq-ws="ws://127.0.0.1:8000"
    data-user-id="1234567890"
    data-fsm-def="simple_fsm"
    data-widget-config-id="1"
    data-conversation-id="1"
    data-title="Hello there 👋"
    data-subtitle="How can we help you?"
    data-lang="es"
    data-preview-mode
    data-custom-css=":root { --chatfaq-color-primary-200: red; }"
    data-hide-sources
    data-sources-first
    data-start-with-history-closed
    data-start-small-mode
    data-full-screen
    data-disable-day-night-mode
    data-only-chat
    data-fit-to-parent
    data-stick-input-prompt
    data-speech-recognition
    data-speech-recognition-auto-send
    data-allow-attachments
    data-initial-conversation-metadata='{"hello": "world"}'
    data-custom-iframed-msgs='{"iframe": {"src": "https://localhost:3000/iframed-msg", "mobileNoMargins": true, "desktopNoMargins": true, "fullWidth": true, "dynamicHeight": true, "scrolling": "np", "noPadding": true}}'
    data-auth-token="1234567890"
    data-enable-logout
    data-enable-resend
></chatfaq-widget>
```

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

You can find the full list of variables on [assets/styles/_variables.css](assets/styles/_variables.css)
