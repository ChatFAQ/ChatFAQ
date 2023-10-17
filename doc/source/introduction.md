# Introduction

## Installation

The system comprises three main components that you need to install:

![ChatFAQ Components](./_static/images/chatfaq_components.png)


- The back-end (<a href="/en/latest/modules/install/index.html#back-installation">install</a>) manages the communication between all the components. It also houses the database for storing all the data related to the chatbots, datasets, models, etc...


- The SDK (<a href="/en/latest/modules/install/index.html#sdk-installation">install</a>) launches a Remote Procedure Call (RPC) server to execute transitions and events from the posted FSM definitions.


- The widget (<a href="/en/latest/modules/install/index.html#widget-installation">install</a>) is a JS browser client application from which the user interacts with the bot.

## Model Configuration

After setting up the components, you will probably want to configure a model that you want to use for your chatbot. Typically the model will be used from the SDK, from a state within its FSM.

Here is an example of a minimum model ([configuration](./modules/configuration/index.md))

## Quick Start

Learning <a href="/en/latest/modules/sdk/index.html#usage">how to use the SDK</a> is the only requirement to start building your own chatbots with ChatFAQ.
