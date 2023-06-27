## [![Group 403 (1)](https://github.com/ChatFAQ/ChatFAQ/assets/127191313/445f5cf9-c557-4529-9d94-a61839d3bb83)](https://www.chatfaq.io/) - The GPT alternative Open Source chatbot!

An open-source conversational search platform as an alternative to commercial GPT solutions:

- Redefine your customer engagement with a generative-AI assistant
- Designed to scale in your complex business ecosystem  today
- Architected to stay in control
- 100% secure

## Development environment setup
3 docker compose files are provided:
- docker-compose.yaml: defines the structure of the whole project, and the relationships between components
- docker-compose.vars.yaml: used to inject the local .env files in the containers
  - to be able to share the .env files without modification between your host computer (process running in a virtualenv
    in your dev computer) and containers, the only thing required is that the services can talk to each other. To accomplish
    that, you can set up your local DNS resolver (file /etc/hosts) to alias the services hostnames to localhost
    - example:
        ```shell
        cat /etc/hosts
        # [... default stuff ...]
        # dev
        127.0.0.1       postgres
        127.0.0.1       back
        ```
- docker-compose.dev-network.yaml: exposes containers to the host, bypassing the isolation rules in the 1st compose files.
  - This one is used to expose services running in containers to the host. This way, for example, `postgres` will be
    accessible to your host on port 5432, combined with the change in `/etc/hosts`, will make the `DATABASE_URL` env var the same
    for both envs: `psqtgresql://user:password@postgres:5432/database`, where `user`, `password` and `database` are defined
    in a `.env` files in the `back` service folder, and apply only to *your* development setup.
