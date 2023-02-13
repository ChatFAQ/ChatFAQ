# ChatFAQ Plugin

This is a simple implementation of a client chatbot that connect to a ChatFAQ's back-end server and offers a interface to communicate with a selected FSM

## Setup

Make sure to install the dependencies:

```bash
# yarn
yarn install

# npm
npm install

# pnpm
pnpm install
```

## Development Server

Start the development server on http://localhost:3000

```bash
npm run dev
```

## Production

Build the application for production:

```bash
npm run build
```

Locally preview production build:

```bash
npm run preview
```

Check out the [deployment documentation](https://nuxt.com/docs/getting-started/deployment) for more information.

## Configuration

Create a *.env* file with 2 variables: **CHATFAQ_BACKEND_API** & **CHATFAQ_BACKEND_WS**. If you are developing locally you could just copy the content of [.envexample]([./.envexample])

## Usage

The idea is just to include a script tag pointing to this service in any external webpage that requires a chatbot interface.

So, in case you are developing locally:

```html
<script src="http://localhost:3000/js/IframeLoader.js"></script>
```

should be enough.

Navigating to http://localhost:3000/ serves a blank page with the example script tag above appended to the body.
