## [![Group 403 (1)](https://github.com/ChatFAQ/ChatFAQ/assets/127191313/445f5cf9-c557-4529-9d94-a61839d3bb83)](https://www.chatfaq.io/) - An Open Source LLM ecosystem for your business needs

**ChatFAQ** is an open-source comprehensive platform for creating a wide variety of chatbots:
- generic ones,
- business-trained,
- or even capable of redirecting requests to human operators.

**ChatFAQ** is a solution that:
- Converts FAQ content into interactive chatbots
- Uses **open source large language models**,
- Provide flexibility and **costs-effectiveness**.

It includes a **specialized NLP/NLG engine** and customized chat widgets,
ensuring a tailored experience for users and avoiding vendor lock-in.


https://github.com/ChatFAQ/ChatFAQ/assets/127191313/7927f51f-d7ac-40e5-b4d0-62081742de4f


The solution comprises three main components although only one (the back-end) is required to be installed:

- [Back-end](back/README.md): This is ChatFAQ's core component, the orchestrator of ChatGPT. It manages client-to-messaging platform connections, session storage, datasets and models registration, FSM registration, FSM executions (intended only for simple FSMs), etc...


- [SDK](sdk/README.md): For those chatbots with complex FSM behaviours, you will probably want to run them on a separate process, that is what for the SDK is made for. Its primary function is to execute the FSM's computations (transition's conditions and states) by running Remote Procedure Call (RPC) server that listen to the back-end requests.


- [Widget](widget/README.md): We built for you a custom front-end solution just so you can talk with your chatbot from the browser using an app you own. Although you can also connect any other message platform as such WhatsApp, Telegram, Signal, Facebook messenger, etc... ChatFAQ supports them all and if it doesn't it can easily be extended to do so.

There also is a CLI tool to help interfacing with the back-end server.

- [CLI](cli/README.md): is a command-line interface to the back-end server. It connects to it and allows you to do anything the back-end server can do but from the confort of your terminal.

- **Admin**: The back-end server comes with a web interface to help you manage your chatbots, datasets, models, etc...

### Visit Us!

For more information about ChatFAQ and any additional needs, feel free to visit our [website](https://www.chatfaq.io/)

<img src="https://assets-global.website-files.com/6257adef93867e50d84d30e2/636e0a6918e57475a843f59f_icon_clyde_black_RGB.svg" alt="logo_discord" width="25"> Or chat with us on [Discord](https://discord.gg/szXJkRXS) for any requests or inquiries about this repository.


<div align="center">
  <img src="https://uploads-ssl.webflow.com/649164df52b043f1d5307b14/64a2c8b1643f13e58e9c0fd0_redes-p-500.webp" alt="logo_redes">
</div>
