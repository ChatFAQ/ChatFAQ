ChatFAQ
=======

Wikipedia Auto-generated from [![](https://github.com/favicon.ico) ChatFAQ/ChatFAQ](https://github.com/ChatFAQ/ChatFAQ) by Mutable.ai Auto Wiki

The ChatFAQ repository implements an end-to-end platform for building conversational AI assistants and chatbots. At its core, it provides services and frameworks for managing conversations and connectivity. The main components are:

The backend implements core services like [Message Handling](#11-message-handling), [State Management](https://github.com/ChatFAQ/ChatFAQ#33-state-management), and [User Management](https://github.com/ChatFAQ/ChatFAQ#13-user-management) using Django, Celery, Channels, and PostgreSQL. It handles receiving and routing messages between services and persists conversation state and data. The [REST APIs](https://github.com/ChatFAQ/ChatFAQ#16-rest-apis) expose CRUD operations on models. Components like [Abstract Components](https://github.com/ChatFAQ/ChatFAQ#17-abstract-components) provide reusable building blocks.

The conversational modeling components focus on generating responses by [Retrieval](https://github.com/ChatFAQ/ChatFAQ#21-retrieval) of relevant contexts from a knowledge base and using those to guide [Response Generation](https://github.com/ChatFAQ/ChatFAQ#response-generation). [Knowledge Extraction](https://github.com/ChatFAQ/ChatFAQ#knowledge-extraction) structures documents, while [Intent Detection](https://github.com/ChatFAQ/ChatFAQ#intent-detection) clusters queries into summarized intents. [Embedding Models](https://github.com/ChatFAQ/ChatFAQ#embedding-models) generate vector representations of text for retrieval.

The [Administrative Interface](https://github.com/ChatFAQ/ChatFAQ#administrative-interface) provides monitoring, configuration, and user management functionality through encapsulated [Components](https://github.com/ChatFAQ/ChatFAQ#31-components) rendered into [Pages](https://github.com/ChatFAQ/ChatFAQ#32-pages) with global [State Management](https://github.com/ChatFAQ/ChatFAQ#33-state-management). [Assets](https://github.com/ChatFAQ/ChatFAQ#35-assets) handle styles and images.

The [Command Line Interface](https://github.com/ChatFAQ/ChatFAQ#command-line-interface) allows managing knowledge objects and configurations. The [Chatbot SDK](https://github.com/ChatFAQ/ChatFAQ#chatbot-sdk) provides tools for building conversational [FSMs](https://github.com/ChatFAQ/ChatFAQ#backend-functionality) using a backend service. The customizable [Embeddable Chat Widget](https://github.com/ChatFAQ/ChatFAQ#embeddable-chat-widget) handles messaging and connectivity.

Overall, ChatFAQ provides services, APIs, and tools for developing conversational AI assistants and chatbots using modern frameworks like Django and Vue.js. It focuses on connectivity, state management, user interfaces, and conversational modeling components.

<details>
<summary>Index</summary>

1. [Backend Functionality](#backend-functionality)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[1.1 Message Handling](#11-message-handling)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[1.2 Data Storage](#12-data-storage)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[1.3 User Management](#13-user-management)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[1.4 Configuration](#14-configuration)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[1.5 Utilities](#15-utilities)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[1.6 REST APIs](#16-rest-apis)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[1.7 Abstract Components](#17-abstract-components)

2. [Conversational Modeling](#conversational-modeling)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[2.1 Retrieval](#21-retrieval)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[2.2 Response Generation](#22-response-generation)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[2.3 Knowledge Extraction](#2.3-knowledge-extraction)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[2.4 Intent Detection](#24-intent-detection)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[2.5 Embedding Models](#25-embedding-models)

3. [Administrative Interface](#administrative-interface)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[3.1 Components](#31-components)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[3.2 Pages](#32-pages)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[3.3 State Management](#33-state-management)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[3.4 Layouts](#34-layouts)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[3.5 Assets](#35-assets)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[3.6 Utilities](#36-utilities)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[3.7 Middleware](#37-Middleware)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[3.8 Plugins](#38-plugins)

4. [Command Line Interface](#command-line-interface)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[4.1 CLI Functionality](#41-cli-functionality)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[4.2 Knowledge Management](#42-knowledge-management)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[4.3 Conversations](#43-conversations)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[4.4. Reviews](#44-reviews)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[4.5 RAG Configuration](#45-rag-configuration)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[4.6 Human Senders](#46-human-senders)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[4.7 Configuration](#47-configuration)


5. [Chatbot SDK](#chatbot-sdk)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[5.1 SDK Core Functionality](#51-sdk-core-functionality)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[5.2 SDK Examples](#52-sdk-examples)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[5.3 SDK Configuration](#53-sdk-configuration)


6. [Embeddable Chat Widget](#embeddable-chat-widget)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[6.1 Widget Functionality](#61-widget-functionality)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[6.2 Chat Interface](#62-chat-interface)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[6.3 State Management](#63-state-management)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[6.4 Sidebar Menu](#64-sidebar-menu)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[6.5 Styles](#65-styles)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[6.6 Utilities](#66-utilities)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[6.7 Plugins](#67-plugins)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[6.8 Internationalization](#68-internationalization)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[6.9 Entry Points](#69-entry-points)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[6.10 Generic Components](#610-generic-components)

7. [Documentation](#documentation)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[7.1 Backend Functionality](#71-backend-functionality)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[7.2 Conversational Modeling](#72-conversational-modeling)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[7.3 Administrative Interface](#73-administrative-interface)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[7.4 Command Line Interface](#74-command-line-interface)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[7.5 Embeddable Chat Widget](#75-embeddable-chat-widget)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[7.6 Core Documentation](#76-core-documentation)

</details>



## 1. Backend Functionality
---------------------

The core backend functionality centers around routing messages between services using the […/broker](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/apps/broker) application. This application handles receiving messages from various sources via subclasses of […/http.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/common/abs/bot_consumers/http.py) and […/ws.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/common/abs/bot_consumers/ws.py), which provide a common interface for HTTP and WebSocket consumers. Messages are modeled using classes like from […/message.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/apps/broker/models/message.py), which represents conversations and the messages within them.

Key components for routing messages include:

*   The /bots subdirectory of […/consumers](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/apps/broker/consumers), which contains classes that handle incoming messages from different platforms. These subclasses abstract away platform details.

*   Classes in files like […/__init__.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/apps/broker/consumers/__init__.py), which contains a class that manages websocket connections and associates them with user IDs.

Finite state machines (FSMs) are implemented in […/fsm](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/apps/fsm) to model conversational flows. Models in […/models.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/apps/fsm/models.py) store FSM definitions and cached conversation states.

The […/common](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/common) directory provides reusable abstractions and components. For example, […/bot_consumers](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/common/abs/bot_consumers) contains base classes like that define a common interface for bot consumers to inherit, focusing their code on application logic. Models, serializers, and viewsets in other files provide a consistent data representation.

`*References: [back/back](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back)*`

### 1.1 Message Handling

The main functionality for handling incoming messages is implemented in the […/consumers](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/apps/broker/consumers) directory. This directory contains classes that handle receiving messages from various sources and routing them to the appropriate bot logic.

The […/bots](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/apps/broker/consumers/bots) subdirectory contains consumer classes for different platforms.

Handlers in […/__init__.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/apps/broker/models/__init__.py) validate incoming data and set associations in the database to route future messages.

The serializers in […/messages](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/apps/broker/serializers/messages) convert payloads between external formats and the internal MML format, allowing different sources to be integrated consistently. Subclasses select the correct serializer.

References: [back/back/apps/broker](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/apps/broker)

### 1.2 Data Storage

References: [back/back/apps/broker/models](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/apps/broker/models), [back/back/apps/broker/migrations](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/apps/broker/migrations)

The core functionality of persisting models and evolving the database schema over time is handled through Django database migrations stored in files like […/0001_initial.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/apps/broker/migrations/0001_initial.py). Migrations provide a consistent and reversible way to modify the database schema during development and when adding new features over time.

Some important migration files:

*   […/0001_initial.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/apps/broker/migrations/0001_initial.py) establishes the initial schema.
    
*   Files like […/0003_platformbot.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/apps/broker/migrations/0003_platformbot.py) add new models over time.
    
*   […/0009_alter_platformconfig_platform_meta.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/apps/broker/migrations/0009_alter_platformconfig_platform_meta.py) and […/0028_alter_adminreview_data.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/apps/broker/migrations/0028_alter_adminreview_data.py) show how fields can be modified non-destructively over time.
    

Files in migration files follow a chronological pattern of smaller incremental changes composed into larger reworks of relationships and schemas over time.

### 1.3 User Management

References: [back/back/apps/people](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/apps/people)

The […/people](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/apps/people) directory implements core user account, authentication, and permission functionality. It contains models, views, serializers, and other code for managing users and their associated permissions.

The model in […/models.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/apps/people/models.py) represents application users. It overrides several default Django user fields and uses a custom class to handle account creation. The class normalizes email addresses and manages group permissions for new users. When a user is saved, it checks permissions and adds the user to groups as needed.

Authentication flows are handled by views in […/views.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/apps/people/views.py). It extends Knox's login functionality to support remember me cookies. Other viewsets in this file provide the REST API for common tasks like retrieving the current user.

Serializers in […/serializers.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/apps/people/serializers.py) handle serializing models and other model data for the APIs. For example, the serializer returns a minimal representation of an authenticated user.

The admin site integration in […/admin.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/apps/people/admin.py) allows managing users via Django's admin interface. Custom management commands like the command in […/createsuperuser.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/apps/people/management/commands/createsuperuser.py) extend default functionality, cleaning input and validating fields.

Migrations like those in […/migrations](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/apps/people/migrations) evolve the database schema, for example to add new user fields over time. URL routing in […/urls.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/apps/people/urls.py) exposes the REST APIs.

### 1.4 Configuration

References: [back/back/config](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/config)

The […/config](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/config) directory centralizes configuration for major frameworks and services used in the ChatFAQ backend Django project. Files in this directory configure important tools like Celery, Channels, ASGI, and Django itself.

The […/celery.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/config/celery.py) configures a Celery app object for running asynchronous tasks. It loads Django settings into Celery's configuration using namespaces. This allows accessing settings directly from Django.

The […/asgi.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/config/asgi.py) defines routing and middleware for ASGI to handle both HTTP and WebSocket requests. A router routes requests based on protocol to the appropriate handler. Middleware applies authentication. Custom middleware performs authentication on WebSocket requests while validation validates origins.

The […/routing.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/config/routing.py) contains routing configuration for WebSocket and HTTP endpoints. A registry automatically registers bot consumers to routes via inheritance, allowing new consumers without changes.

The […/settings.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/config/settings.py) contains all important Django project configuration and settings. It defines a custom preset class that overrides environment variable handling depending on the cloud provider. A context populates settings from environment variables.

The […/urls.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/config/urls.py) contains URL routing configuration. It configures the admin site and defines main URL patterns including login/logout views and API URLs.

### 1.5 Utilities

References: [back/back/utils](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/utils)

This section covers common utilities used throughout the backend code for authentication, Celery, Channels, and logging functionality.

Authentication is handled by functions in the […/auth.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/utils/auth.py) file. The main function persists a user's ID and backend in the session, allowing them to stay logged in across requests. The class extends Django's authentication to support logging in via a "remember me" cookie.

Celery task handling and configuration is abstracted in […/celery.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/utils/celery.py). This file checks that each worker has a dedicated queue, and provides a function to trigger recaching language models in a distributed way.

Channels messaging is customized via classes in […/custom_channel_layer.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/utils/custom_channel_layer.py). The class overrides the base channel layer to ensure message ordering when sending to groups.

Logging is customized by the class in […/logging_formatters.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/utils/logging_formatters.py). This class overrides the method to add additional fields like timestamps to structured JSON logs.

### 1.6 REST APIs

References: [back/back/apps/broker/views](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/apps/broker/views)

The […/__init__.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/apps/broker/views/__init__.py) file exposes common operations on models through REST API endpoints defined by generic class-based views. Generic class-based views handle routing requests to methods and serialization automatically based on the actions. This provides a clean interface without much additional code.

### 1.7 Abstract Components

References: [back/back/common/abs](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/common/abs)

The directory […/abs](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/common/abs) provides reusable components for building bot consumers and finite state machines (FSMs). It contains abstract base classes that define common functionality for these components to inherit from.

The subdirectory […/bot_consumers](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/common/abs/bot_consumers) contains abstract base classes for implementing bot consumers. The file […/__init__.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/common/abs/bot_consumers/__init__.py) defines the base class that all consumers inherit from. It provides properties and methods for core tasks like interacting with conversations, users, and FSMs.

These classes separate concerns for handling requests and responses from focusing on bot logic.

## 2. Conversational Modeling
-----------------------

References: [chat_rag/chat_rag](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/chat_rag/chat_rag)

The core functionality implemented in the […/chat_rag](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/chat_rag/chat_rag) directory coordinates an end-to-end workflow for conversational modeling. This involves retrieving relevant contexts from a knowledge base to guide response generation.

The /__init__.py file coordinates this workflow by initializing a class. The class's method handles retrieving new candidate contexts by calling functions in […/inf_retrieval](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/chat_rag/chat_rag/inf_retrieval) to get, rank, and filter contexts. It then calls methods on the attributes to generate a response using the updated contexts.

The […/data](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/chat_rag/chat_rag/data) subdirectory contains functionality for parsing unstructured documents into structured knowledge items. Functions split text into chunks using various splitting classes defined in […/splitters.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/chat_rag/chat_rag/data/splitters.py).

The […/inf_retrieval](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/chat_rag/chat_rag/inf_retrieval) subdirectory implements key information retrieval tasks. The class defined in […/semantic_retriever.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/chat_rag/chat_rag/inf_retrieval/retrievers/semantic_retriever.py) performs semantic retrieval by encoding queries and contexts to compute scores and return top matches. The function defined in […/check_answ_questions.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/chat_rag/chat_rag/inf_retrieval/check_answ_questions.py) identifies answerable questions, while the class defined in […/query_generator.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/chat_rag/chat_rag/inf_retrieval/query_generator.py) constructs prompts to generate questions. The file […/cross_encoder.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/chat_rag/chat_rag/inf_retrieval/cross_encoder.py) contains functions.

The […/intent_detection](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/chat_rag/chat_rag/intent_detection) subdirectory clusters similar queries into intents using functions defined in files. Functions defined in files generate summarized intents for each cluster.

The […/llms](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/chat_rag/chat_rag/llms) subdirectory contains classes that provide a common interface to initialize, load, and interact with different large language models for response generation, such as classes defined in files.

### 2.1 Retrieval

References: [chat_rag/chat_rag](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/chat_rag/chat_rag), [chat_rag/chat_rag/inf_retrieval](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/chat_rag/chat_rag/inf_retrieval)

The […/inf_retrieval](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/chat_rag/chat_rag/inf_retrieval) directory handles retrieving relevant contexts from a knowledge base to guide response generation. It contains several important components for this task:

*   Embedding models like in […/base_model.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/chat_rag/chat_rag/inf_retrieval/embedding_models/base_model.py) are used to generate fixed-size embeddings from texts. This allows comparing passages efficiently.
    
*   The semantic retrieval functionality is implemented in the class in […/semantic_retriever.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/chat_rag/chat_rag/inf_retrieval/retrievers/semantic_retriever.py). Its main method encodes queries and computes scores against contextual embeddings, returning the top matches.
    
*   Context data for matches is extracted by a method.
    
*   For efficiency, a method retrieves contexts in batches rather than all at once.
    
*   A method ties everything together, returning complete context data for a query.
    

Other files generate embeddings, questions, and check if questions can be answered based on passage similarity scores.

The components work together to retrieve knowledge that can guide coherent response generation.

### 2.2 Response Generation

References: [chat_rag/chat_rag/llms](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/chat_rag/chat_rag/llms)

The […/llms](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/chat_rag/chat_rag/llms) directory contains implementations of different large language models (LLMs) for conversational modeling. It provides a common interface to initialize, load, and interact with pre-trained LLMs from various sources through subclasses that inherit from an abstract base class defined in […/base_llm.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/chat_rag/chat_rag/llms/base_llm.py).

The subclasses define methods to condition responses on retrieved contexts and user input. The […/claude_client.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/chat_rag/chat_rag/llms/claude_client.py) subclass interfaces with Anthropic's LLMs by calling their APIs and formatting the prompt before passing to the LLM.

The […/openai_client.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/chat_rag/chat_rag/llms/openai_client.py) client passes prompts to the OpenAI API to retrieve responses.

The […/hf_llm.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/chat_rag/chat_rag/llms/hf_llm.py) loads HuggingFace models and defines methods to encode, pass and decode prompts through the model.

The […/mistral_client.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/chat_rag/chat_rag/llms/mistral_client.py) inherits from another class and formats prompts before calling the Mistral API client to handle generation.

### 2.3 Knowledge Extraction

References: [chat_rag/chat_rag/data](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/chat_rag/chat_rag/data)

The […/data](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/chat_rag/chat_rag/data) directory contains code for extracting structured knowledge from unstructured documents that can be used by Retrieval Augmented Generation models. The main functionality includes parsing documents like PDFs and HTML into a structured representation using parser functions.

Documents are parsed into objects representing sections, titles, and other elements. A class represents a single item of extracted knowledge, with fields like content, title, and URL.

Text content is split into meaningful chunks using various splitter classes. Parser functions handle the full parsing workflow. Main parser functions wrap these steps.

### 2.4 Intent Detection

References: [chat_rag/chat_rag/intent_detection](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/chat_rag/chat_rag/intent_detection)

The […/intent_detection](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/chat_rag/chat_rag/intent_detection) directory contains code for detecting intents from user queries by clustering similar queries and generating summarized intents. The file […/clusterize_text.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/chat_rag/chat_rag/intent_detection/clusterize_text.py) contains functionality for clustering queries. The file […/gen_intent.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/chat_rag/chat_rag/intent_detection/gen_intent.py) contains functionality for generating summarized intents.

### 2.5 Embedding Models

References: [chat_rag/chat_rag/inf_retrieval/embedding_models](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/chat_rag/chat_rag/inf_retrieval/embedding_models)

The […/embedding_models](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/chat_rag/chat_rag/inf_retrieval/embedding_models) directory contains implementations of embedding models that can be used to generate fixed-size vector representations of text for downstream tasks like semantic search.

/__init__.py imports classes to make them available to the package. The classes implement generating embeddings from text using pretrained models, allowing embeddings to be used for downstream tasks like search and retrieval.

## 3. Administrative Interface
------------------------

References: [admin](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin)

The administrative interface allows administrators to monitor and manage key aspects of the ChatFAQ system. It provides a centralized dashboard for configuration, user management, and viewing task histories.

The […/pages](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/pages) directory contains Vue components that define different pages for the interface.

State management is centralized using Pinia stores defined in /store.

Many components in /components are reused across pages.

The UserManagement.vue component manages the user interface using tabs. It fetches user data from an API to display in tables or forms.

Styles are defined modularly. Global styles are set in /assets/styles/global.scss. Variables, mixins and helpers reused across styles live in /assets/styles/reusable/ to promote consistency.

The WidgetConfig.vue component loads schemas from an API via the store to generate customizable configuration interfaces. It displays options in tabbed sections and renders custom fields using child components.

The AIConfig.vue component provides a centralized interface to configure different AI model types. It uses tabs to separate configurations. Forms allow updating settings by calling methods that submit to APIs.

### 3.1 Components

References: [admin/components](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/components)

The core UI components in the ChatFAQ admin interface are defined in the […/components](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/components) directory. This directory contains several subdirectories that encapsulate reusable Vue components for specific parts of the admin views.

Some key subdirectories and their purposes are:

*   […/generic](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/components/generic): Provides base components for common tasks like form rendering, CRUD operations, and navigation that are used across different views and forms.
    
*   […/menu](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/components/menu): Implements the sidebar menu UI through the […/MenuItem.vue](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/components/menu/MenuItem.vue) component.
    
*   […/labeling](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/components/labeling): Contains components for labeling conversations.
    
*   […/fields](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/components/user_management/fields): Securely handles editing user fields.
    
*   […/fields](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/components/widget_config/fields): Provides field components reused in configuration forms like […/ColorField.vue](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/components/widget_config/fields/ColorField.vue).
    

Many components abstract common logic. Pinia stores also centralize state management. For example, stores manage data.

### 3.2 Pages

References: [admin/pages](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/pages)

The Vue components defined in the […/pages](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/pages) directory handle routing and rendering UI components into pages for the administrative interface. Key pages include:

The […/dashboard.vue](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/pages/dashboard.vue) component renders the dashboard page. It handles routing and likely displays metrics, activity, and configuration options.

The […/task_history.vue](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/pages/task_history.vue) component renders functionality to display task history details. It likely fetches data from an API and displays it with filters and pagination.

The […/labeling.vue](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/pages/labeling.vue) component renders functionality for the labeling workflow. It allows labeling examples with different categories using logic to fetch examples and apply labels.

The […/user_management.vue](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/pages/user_management.vue) component renders functionality to display and manage user accounts. It likely fetches user data and allows viewing, editing, and deleting users.

The […/widget_config.vue](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/pages/widget_config.vue) component renders a form to configure widget options. It manages the configuration state and calls methods to persist the data.

### 3.3 State Management

References: [admin/store](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/store)

The […/store](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/store) directory centralizes state management for the admin interface using Pinia stores. It contains two stores defined in files:

1.  The […/auth.js](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/store/auth.js) file defines a store to manage authentication state.
    
2.  The […/items.js](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/store/items.js) file defines a store to manage item data.
    

The items store state tracks items, paths, the OpenAPI schema, and loading/editing states.

The action fetches all items for a given API URL from the server and stores them in the state. It allows dynamic ordering. The action deletes an item by ID from the server and refetches to update the local state. The action fetches the OpenAPI schema from the server and stores it in the state, providing metadata about APIs and resources. The getter looks up a schema definition from the loaded schema by name or API path, also resolving JSON schema references. The methods get an item/items matching a filter either from local state or by fetching from the server.

The auth store tracks authentication status with a boolean and defines methods to log in and log out. On login, it makes an API request, saves the returned token, and sets the authenticated state to true. Logout clears the auth token and sets authenticated to false.

By encapsulating critical state management logic in these centralized, accessible stores, it coordinates data fetching, caching responses, and loading states. The stores also provide a single source of reactive state for components via Pinia.

### 3.4 Layouts

References: [admin/layouts](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/layouts)

The Vue layout components defined in the […/layouts](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/layouts) directory provide consistent structures for admin pages. The […/default.vue](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/layouts/default.vue) layout renders a navigation component from ~/components/navbar/Navbar.vue, and contains a element for main page content. It also renders an active tasks component from ~/components/task_history/ActiveTasks.vue.

Styles are defined with scoped CSS to position these sections. The layout utilizes common navigation and tasks components, while […/empty.vue](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/layouts/empty.vue) provides a blank canvas. This separation of concerns makes the code more maintainable and reusable.

### 3.5 Assets

References: [admin/assets](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/assets)

The […/assets](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/assets) directory contains files that define styles, fonts and images used in the ChatFAQ administrative interface. It implements a standardized structure and tools to promote consistent visual styling across components.

The […/styles](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/assets/styles) directory contains cascading style sheets that define global styles, variables and mixins. The […/settings.colors.scss](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/assets/styles/settings/settings.colors.scss) file defines color variables for common colors, states, and brand colors. New variables are introduced for a primary green color scheme. The […/settings.global.scss](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/assets/styles/settings/settings.global.scss) file defines font styles and breakpoint widths for responsive design.

The […/reusable](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/assets/styles/reusable) subdirectory aims to provide reusable styles and consistency across components. It contains style mixins, functions and helpers for tasks like breakpoints, colors and typography. The […/el_plus](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/assets/styles/el_plus) directory contains stylesheets from the Element UI component library, including the main style sheet […/_globals.scss](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/assets/styles/el_plus/_globals.scss).

The […/_fonts.scss](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/assets/styles/_fonts.scss) file defines font faces, specifying styles, ranges and sources for each font. The […/_variables.scss](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/assets/styles/_variables.scss) file defines variables for colors, fonts, sizes and breakpoints. By defining variables, mixins and helpers, the directory structure promotes consistent visual styling that is easy to manage across components.

### 3.6 Utilities

References: [admin/utils](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/utils)

This section covers helper functions and libraries that provide common utilities for other parts of the codebase to use. The […/utils](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/utils) directory contains functionality for color conversion.

The […/index.js](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/utils/index.js) file contains functionality to convert color values between formats.

### 3.7 Middleware

References: [admin/middleware](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/middleware)

Middleware handles authentication and authorization for routes in the admin interface. The […/middleware](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/middleware) directory centralizes middleware used for this purpose.

The main middleware checks authentication state using a store. If authenticated, it prevents navigating to the 'login' route and instead redirects to the home page. If not authenticated, it prevents navigation to any other route and redirects to the login page.

The key parts are importing a function from the store to check auth state, defining a middleware function, checking the auth state, and conditionally redirecting using functions. This provides a centralized way to enforce auth rules during routing. By leveraging the store for auth state and checking it in the middleware, common authentication workflows can be implemented like redirecting logged in users from the login page and non-logged in users from protected pages.

### 3.8 Plugins

References: [admin/plugins](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/plugins)

The […/plugins](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/plugins) directory registers plugins that provide globally available functionality throughout the Nuxt application. The /elementIcons.js plugin registers all icon components from the Element Plus icon library, making them globally available in Nuxt. It imports all icon components and registers each one on the Nuxt app instance using the component name.

The /i18n.js plugin defines internationalization functionality. It imports English translation data from /locales/en.json and uses a library to create an i18n instance. The plugin function exports a default Nuxt plugin that takes the app instance and registers the i18n instance, making i18n available globally in Vue.

The /elementIcons.js plugin loops through each imported icon component from Element Plus. It registers each component on the Nuxt app instance using the icon name as the component name. This allows any Vue component to reference icon components directly, such as . No other classes or functions are defined in this file.

The /i18n.js plugin imports a function to initialize an i18n instance. It imports English translations from /locales/en.json and passes them to the initialization function along with the configuration. This function encapsulates i18n instance creation. The exported plugin function registers the i18n instance on the app instance, making translation available globally in Vue.

## 4. Command Line Interface
----------------------

References: [cli/chatfaq_cli](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/cli/chatfaq_cli)

The […/chatfaq_cli](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/cli/chatfaq_cli) directory provides a command line interface (CLI) for interacting with the ChatFAQ knowledge management system. At the top level, it defines a Python application using the Typer framework. The […/__init__.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/cli/chatfaq_cli/__init__.py) file initializes the CLI and registers subcommands from other modules.

Authentication is handled via a class defined in […/__init__.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/cli/chatfaq_cli/__init__.py), which stores an authentication token read from the configuration.

Modules in […/data](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/cli/chatfaq_cli/data) define subcommands for common knowledge management tasks. For example, […/intents.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/cli/chatfaq_cli/data/intents.py) contains commands for intent operations. These modules interact with the API by calling methods.

The […/rag_pipeline](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/cli/chatfaq_cli/rag_pipeline) directory defines subcommands to configure RAG pipeline components like retrievers and generation configs. Modules make requests to configure these models.

Configuration is handled via functions in […/__init__.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/cli/chatfaq_cli/helpers/__init__.py), which read and write to a JSON file. The CLI provides a unified interface while delegating to the ChatFAQ API and external services.

### 4.1 CLI Functionality

References: [cli/chatfaq_cli](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/cli/chatfaq_cli), [cli/chatfaq_cli/helpers](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/cli/chatfaq_cli/helpers)

The main CLI application functionality is implemented in […/__init__.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/cli/chatfaq_cli/__init__.py). This file defines a Typer CLI application instance and registers subcommands from other modules. It retrieves configuration values needed by CLI commands.

Configuration values are read from and written to a JSON file at ~/.chatfaq-cli-config .

Common utilities like CLI argument parsing and output formatting are provided by libraries like Typer and Rich which are used across modules. Typer builds the CLI structure and parses arguments. Rich handles output formatting.

Some key CLI modules include […/data](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/cli/chatfaq_cli/data) which defines commands for knowledge management tasks by calling functions implemented in the module. The […/__init__.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/cli/chatfaq_cli/conversations/__init__.py) file provides functions for interacting with conversations.

### 4.2 Knowledge Management

References: [cli/chatfaq_cli/data](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/cli/chatfaq_cli/data)

The […/data](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/cli/chatfaq_cli/data) directory contains modules that define commands for managing knowledge objects through the ChatFAQ CLI. These commands provide a way to interact with the knowledge management functionality of the ChatFAQ API from the command line.

The […/knowledge_items.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/cli/chatfaq_cli/data/knowledge_items.py) module implements commands for knowledge items. Knowledge items represent pieces of structured knowledge that can be associated with a knowledge base.

The […/titles.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/cli/chatfaq_cli/data/titles.py) module defines commands for auto-generated title management. These commands call API endpoints by accessing the class defined in […/utils.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/cli/chatfaq_cli/data/utils.py).

The […/knowledge_bases.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/cli/chatfaq_cli/data/knowledge_bases.py) module implements commands to create, list, delete, and download knowledge bases.

The […/intents.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/cli/chatfaq_cli/data/intents.py) module defines commands for intent management. These commands make requests to intent endpoints.

The […/utils.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/cli/chatfaq_cli/data/utils.py) module contains a class which provides a clean interface to make HTTP requests to the REST API for various data entities. It utilizes libraries like requests.

### 4.3 Conversations

References: [cli/chatfaq_cli/conversations](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/cli/chatfaq_cli/conversations)

The […/conversations](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/cli/chatfaq_cli/conversations) directory contains Python files that define specific commands for interacting with conversations via the command line interface. These commands allow viewing, editing, deleting and searching conversations from the CLI.

The main functionality is provided in Python files in the […/conversations](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/cli/chatfaq_cli/conversations) directory. These files provide functions for interacting with conversations. These functions make REST API calls to the backend services via the Redis client imported from the parent CLI context.

The individual command files implement the command line interfaces for functions like viewing conversations. The view conversations command would call the function for viewing conversations, format the response, and display it to the user. This structure provides a clean, organized CLI interface for conversations while reusing the existing REST API implementation. The CLI functionality acts as a thin wrapper over the REST API, avoiding rewriting existing conversation handling logic.

### 4.4. Reviews

References: [cli/chatfaq_cli/reviews](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/cli/chatfaq_cli/reviews)

The […/reviews](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/cli/chatfaq_cli/reviews) directory defines commands for managing reviews of messages. It contains functionality for creating and fetching reviews of messages from the backend broker API.

The file […/__init__.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/cli/chatfaq_cli/reviews/__init__.py) defines functionality for handling reviews.

It uses a class to communicate with the broker API, but the implementation of this class is not defined in the file. The class is imported and used by the file but its implementation is not defined here.

### 4.5 RAG Configuration

References: [cli/chatfaq_cli/rag_pipeline](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/cli/chatfaq_cli/rag_pipeline)

The […/__init__.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/cli/chatfaq_cli/rag_pipeline/__init__.py) file defines a top-level CLI application for configuring RAG pipeline components. It incorporates additional apps defined in other modules for specific configuration tasks.

The […/rag_config.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/cli/chatfaq_cli/rag_pipeline/rag_config.py) module likely contains functions for managing RAG configurations using Typer decorators to build the CLI interface. Functions make requests to external APIs to perform CRUD operations, though no specific logic is described.

The […/retriever_config.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/cli/chatfaq_cli/rag_pipeline/retriever_config.py) module defines CLI commands for configuring retrievers. Functions make requests using a client retrieved from the context, abstracting the backend implementation.

### 4.6 Human Senders

References: [cli/chatfaq_cli/senders](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/cli/chatfaq_cli/senders)

The […/senders](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/cli/chatfaq_cli/senders) directory contains functionality for interacting with human senders via commands in the CLI. The main application class used is the CLI application class.

The core command implemented is for listing all human senders. This is done by the command added to the CLI application class instance. When called, it retrieves the senders by calling the method on the "broker/senders" key of the passed object. This object provides access to wherever senders are stored, such as a database. The result of the method is then printed.

The business logic is contained entirely in the /__init__.py file, which performs the following:

*   Creates an instance of the CLI application class
*   Adds the command via a decorator
*   The command accepts one parameter, an object that provides backend functionality
*   It calls the method on the "broker/senders" key of the passed object
*   The results are printed out

No other classes, functions, or files are implemented within this directory - it relies on the CLI application class and the passed object's methods. This provides a simple but complete interface via CLI commands to retrieve and display human senders by integrating with whatever backend data storage is used.

### 4.7 Configuration

References: [cli/chatfaq_cli/config](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/cli/chatfaq_cli/config)

The […/config](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/cli/chatfaq_cli/config) directory contains functionality for configuring the ChatFAQ CLI. A file defines two commands using the Typer library - one for saving a token string to the configuration, and another for saving a host name string.

The file uses Typer to define commands that take string inputs from the user. A function handles writing these string values to the configuration file. It allows configuring authentication tokens and backend service URLs directly from the CLI.

Typer is used for its capabilities in command line parsing and output formatting with Rich. Strings passed to the commands are saved using a single function, keeping the business logic straightforward. This provides an easy way for users to configure authentication and connection settings without having to manually edit configuration files.

### 5. Chatbot SDK
-----------

References: [sdk](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/sdk)

The ChatFAQ SDK provides functionality for building and running conversational agents using finite state machines (FSMs). The core classes and utilities for defining and executing FSMs are contained in the […/chatfaq_sdk](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/sdk/chatfaq_sdk) directory.

Classes represent states and transitions between states. Functions defined on states or transitions are registered with the SDK. The definition can be serialized.

The class represents a single conversational state. It contains the state's name and lists of functions that will be executed. These functions are where responses are yielded to the user.

The class defines a possible change from one state to another. It contains the destination state, optional source state, and lists of functions that must return a value for the transition to occur.

The class handles connecting a definition to the backend over WebSockets. It registers handlers for requests using a decorator. The send request method sends language model requests to the backend, with responses yielded via a generator.

Layers provide an interface to integrate natural language components into the backend. The layer handles language model requests and responses.

Configuration is contained in /chatfaq_sdk/settings.py. Examples in /examples demonstrate using the SDK.

### 5.1 SDK Core Functionality

References: [sdk/chatfaq_sdk](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/sdk/chatfaq_sdk), [sdk/chatfaq_sdk/fsm](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/sdk/chatfaq_sdk/fsm)

The […/__init__.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/sdk/chatfaq_sdk/__init__.py) file defines the main ChatFAQ class for interacting with the ChatFAQ backend. This class handles connecting to the backend over WebSockets, registering handlers, and sending and receiving RPC and LLM requests.

The ChatFAQ class is initialized with parameters like the backend URL, auth token, and optional FSM definition. It connects to the backend over WebSockets to handle RPCs and LLMs.

A decorator is used to register handler functions for RPC requests from the backend. These handlers can return layers or conditions which are then executed.

Methods establish the WebSocket connections and send LLM requests to the backend. Callbacks handle incoming messages and dispatch them to the appropriate handlers.

The […/conditions](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/sdk/chatfaq_sdk/conditions) directory contains condition subclasses.

### 5.2 SDK Examples

References: [sdk/examples/model_example](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/sdk/examples/model_example), [sdk/examples/simple_example](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/sdk/examples/simple_example)

The examples demonstrate building chatbots using the ChatFAQ SDK by defining finite state machines (FSMs). Two examples are shown - a simple chatbot in […/simple_example](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/sdk/examples/simple_example) and a model-based chatbot in […/model_example](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/sdk/examples/model_example).

The simple chatbot example defines states and transitions between them. Event functions yield responses.

The model-based chatbot similarly defines states that yield responses using functions. Transitions define movement.

Both examples demonstrate the basic building blocks of states, events, transitions, and conditions to define a conversation flow using the SDK. They show initializing an SDK instance and connecting it by importing definitions. The examples provide a starting point for understanding how to build a chatbot using the SDK.

### 5.3 SDK Configuration

References: [sdk/chatfaq_sdk/settings.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/sdk/chatfaq_sdk/settings.py)

The […/settings.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/sdk/chatfaq_sdk/settings.py) file contains functionality for configuring the ChatFAQ SDK. It centralizes the configuration logic. This includes setting log levels and output.

The main configuration logic is contained in a function. This function prepares the SDK by calling other functions to configure logging. It sets the default log output to standard output.

A function handles setting the log output location. It sets the output to standard output by default.

Another function controls the base log levels for different parts of the system. It can override levels for specific external packages if needed, allowing filtering of messages.

By centralizing the configuration in a file and a main function, it provides developers an easy way to prepare the SDK for use without specifying all configuration details. The file also acts as a single source of truth for defaults.

## 6. Embeddable Chat Widget
----------------------

References: [widget](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget)

The core functionality of the embeddable ChatFAQ widget is encapsulated in the [widget](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget) directory. This directory contains all the necessary components to build a customizable chat interface that can be embedded into third party sites.

The main business logic resides in the […/components](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/components) subdirectory. Components handle displaying a chat interface.

State management is centralized in the […/store](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/store) directory. The Pinia store module provides getters for retrieving data and mutations for updating state.

The […/styles](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/assets/styles) directory contains the CSS and Sass files defining the visual styling for the widget interface. Styles are organized into variables, mixins, and global stylesheets. Variables define shared colors, fonts, and sizes, while mixins provide reusable styles.

Configuration and localization are handled by plugins defined in […/plugins](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/plugins). The plugins provide core functionality in a decoupled manner.

Entry points in […/entry.*](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/components/entry.*) register components globally.

In summary, the ChatFAQ widget provides a customizable and embeddable chat interface using modern Vue tools and design patterns for state management, styling, and extensibility.

### 6.1 Widget Functionality

References: [widget/components/Widget.vue](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/components/Widget.vue), [widget/store](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/store)

The […/Widget.vue](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/components/Widget.vue) component manages the main widget UI and business logic. It conditionally renders different parts of the widget based on the state.

The global store at […/index.js](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/store/index.js) manages all application data and state.

The store connects the widget component to the global application state in a uniform way via Pinia. The getter properties process and transform the raw data as needed by different parts of the UI. This encapsulates the business logic and data handling in a clean, centralized manner.

### 6.2 Chat Interface

References: [widget/components/chat](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/components/chat)

The core functionality implemented in the […/chat](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/components/chat) directory is handling the chat interface within the ChatFAQ widget. This includes initializing and managing the WebSocket connection to the backend, sending and receiving messages, and rendering the chat user interface components.

The […/Chat.vue](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/components/chat/Chat.vue) component initializes the WebSocket connection using the ws library. It defines callbacks like handling received messages and connection events. When a message is received, it is added to a messages array. A heartbeat is sent periodically to keep the connection alive.

When the user sends a message, a function constructs a message object and sends it over the WebSocket. It also resets the input.

Scrolling is handled by watching a property and calling a function, which updates the property. This allows auto-scrolling to the bottom when new messages are received.

The […/msgs](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/components/chat/msgs) subdirectory contains components for displaying different types of messages. Components apply styles based on values from the global store.

Components conditionally display referenced content below a message and define a state variable to track expansion/collapse, toggling this on click. Templates and styles reference the global store.

Components render text messages. Computed properties replace Markdown links with HTML links using a regex. Conditional rendering applies styles based on the dark mode value from the store.

A component renders the chat interface elements. It imports the global store and defines handlers for toggling features.

A component displays a loading indicator when messages are loading. It reads states from the global store to style and animate the component.

A component handles collecting and submitting user feedback via API calls. It uses refs to track input state and emits events on submit.

### 6.3 State Management

References: [widget/store](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/store)

The Pinia store defined in […/index.js](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/store/index.js) manages global state for the chatbot application. It exposes properties and methods to retrieve and transform the conversation data held in state.

The store provides a centralized data source managed in a reactive way via Pinia. Properties allow retrieving data from state, like conversations. Methods manipulate the state data, such as fetching from the API or changing conversation names.

Key parts of the store include:

*   Transforming the nested conversation message stacks into flat arrays and grouped objects for display.
    
*   Providing a single source of truth for all application data and state in a reactive way.
    

### 6.4 Sidebar Menu

References: [widget/components/left-menu](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/components/left-menu)

The […/left-menu](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/components/left-menu) directory contains the Vue components that define the left-hand menu sidebar for the ChatFAQ widget. The […/LeftMenu.vue](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/components/left-menu/LeftMenu.vue) component defines the UI layout and integrates with the global Pinia store. It imports reusable menu item components from the /items subdirectory.

The /items subdirectory contains several important reusable menu item components implemented as individual Vue components. The […/DeleteHistory.vue](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/components/left-menu/items/DeleteHistory.vue) component displays a menu item that allows deleting chat history, interfacing with the global store to track deletion state. […/DownloadHistory.vue](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/components/left-menu/items/DownloadHistory.vue) similarly implements a download history menu item. […/NewConversationItem.vue](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/components/left-menu/items/NewConversationItem.vue) defines a simple component for a clickable menu item that dispatches an action to the store to create a new conversation.

The […/MenuItem.vue](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/components/left-menu/items/abs/MenuItem.vue) base component provides consistent styling for menu items via a class, while child components implement specific behavior and data. Watchers in components like […/HistoryItem.vue](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/components/left-menu/items/HistoryItem.vue) update the UI based on changes to the global store state.

### 6.5 Styles

References: [widget/assets/styles](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/assets/styles)

The visual styling for the ChatFAQ widget is defined through CSS and Sass files located in the […/styles](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/assets/styles) directory. This directory contains several important files and subdirectories that work together to establish a consistent and maintainable visual style.

The […/_variables.scss](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/assets/styles/_variables.scss) file centralizes all visual attributes used in the widget's styling. It defines CSS variables for colors, fonts, icons and sizes which are organized into general, specific and Sass variable sections. General sections contain shared colors, fonts and icon paths, while specific sections customize colors for individual elements. Defining variables in this file allows values to be consistently reused across other CSS and Sass files. Gradient colors are generated from start/end variables, while font styles unify typography.

The […/global.scss](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/assets/styles/global.scss) file establishes baseline styling. It imports items from other files, then sets properties on the * selector.

The […/_mixins.scss](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/assets/styles/_mixins.scss) file contains mixins.

The […/_fonts.scss](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/assets/styles/_fonts.scss) file defines a web font by specifying its properties and font data sources.

These files work together to implement a maintainable and reusable approach to visual styling through CSS custom properties, mixins, and abstraction of attributes - promoting consistency across the ChatFAQ widget interface.

### 6.6 Utilities

References: [widget/utils](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/utils)

This section details helper functions contained in the widget utils directory. The […/utils](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/utils) directory contains utility functions that make common tasks easier. It provides a simple way to work with related tasks across code without worrying about low-level implementation details.

### 6.7 Plugins

References: [widget/plugins](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/plugins)

The […/plugins](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/plugins) directory registers plugins for core functionality. The […/index.js](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/plugins/index.js) file handles initialization logic. It exports functions which initialize the libraries.

The plugins make these functions available globally, so their instances can be used by components. This decouples the setup from the registration.

### 6.8 Internationalization

References: [widget/plugins/i18n.js](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/plugins/i18n.js)

The file […/i18n.js](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/plugins/i18n.js) handles internationalization for the widget by configuring translations of UI text into different languages. It imports a function from ./index.js that is responsible for the actual i18n configuration and localization logic. This function creates an instance when called.

The plugin function exports the instance as a constant and installs it on the Vue app instance passed via the context. This makes the instance available as a global plugin for translation in any Vue components. Components can import and use the instance to translate strings as needed.

By defining the plugin in this file, internationalization is configured automatically for all pages and components in the Nuxt app. The abstracted instance handles locating translation text based on the user's language preferences. This allows the widget interface to support multiple languages seamlessly without additional code in each component.

### 6.9 Entry Points

References: [widget/components/entry.js](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/components/entry.js), [widget/components/entry.esm.js](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/components/entry.esm.js)

The files […/entry.js](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/components/entry.js) and […/entry.esm.js](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/components/entry.esm.js) work together to define entry points for building the widget in different environments.

[…/entry.js](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/components/entry.js) exports a plugin that attaches components exported from […/entry.esm.js](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/components/entry.esm.js). This allows the components to be accessed by name when the plugin is installed. It also checks if Vue is globally available, and automatically installs the plugin.

[…/entry.esm.js](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/components/entry.esm.js) first imports components from […/components](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/components). It then defines a function that takes a parameter. The function loops through the components, registering each component using. This makes each component globally available. It exports the function as the default export to allow installation. It also re-exports each individual component for direct registration if needed.

### 6.10 Generic Components

References: [widget/components/generic](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/components/generic)

The […/generic](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/components/generic) directory contains reusable Vue components that are used throughout the ChatFAQ widget. This includes base UI elements like buttons, form controls, loading indicators.

The […/Checkbox.vue](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/components/generic/Checkbox.vue) component defines a customizable checkbox input using SVG graphics. It imports utilities and defines props for customization. A ref is used to track the internal checked state and watch the prop for changes.

The […/Loader.vue](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/components/generic/Loader.vue) component defines a reusable loading indicator. It defines the HTML structure using a template with a class binding. The loading animation is implemented entirely through CSS animations on radial gradients inside the element. A prop controls whether a light or dark color scheme is used.

The /animations subdirectory contains any additional CSS transitions or animations shared between components, though none are defined in the current code.

The /icons subdirectory defines SVG icon components, but without code summaries of the icon components we do not have implementation details.

## 7. Documentation
-------------

References: [doc/source/modules](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/doc/source/modules)

This section documents the core components of the ChatFAQ system. It covers documentation organized by concern in the […/modules](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/doc/source/modules) directory.

This directory contains documentation for several important modules. The /back subdirectory documents the backend system, including an overview of core functionality in /back/index.md.

The /configuration subdirectory describes how to configure an AI assistant using the retrieval and generation pipeline. Key files include /configuration/index.md which discusses the main components like the knowledge base, retrieval configuration, prompt configuration, language model configuration, generation configuration, and combined configuration.

The /installations subdirectory contains documentation for installing the backend, frontend, and SDK components. The /installations/index.md file provides an overview of the installation process.

The /interfaces subdirectory documents the different interfaces that can be used to interact with ChatFAQ's backend data, including the CLI documented in /interfaces/cli.

The /sdk subdirectory documents building and running chatbot Finite State Machines (FSMs) on a separate process via Remote Procedure Calls (RPCs) as described in /sdk/index.md.

### 7.1 Backend Functionality

References: [back/back](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back)

The core backend functionality in the ChatFAQ system is implemented across several key directories and applications. Message handling and routing is a primary concern, with state management also playing an important role.

The […/broker](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/apps/broker) directory implements message brokering functionality. Incoming messages from various sources are received via classes in the /consumers subdirectory. Messages are modeled and stored using the model defined in /models/message.py. Views in /views expose REST APIs to interact with stored messages.

The […/fsm](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/apps/fsm) application implements state management using finite state machines (FSMs). The model and model defined in /models.py store named FSM definitions and the current state for individual conversations. Models, views, and serializers provide interfaces to define, retrieve, update and query FSM states.

Common abstractions are defined in […/common](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/common). Utilities in […/utils](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/utils) handle common tasks.

### 7.2 Conversational Modeling

References: [chat_rag/chat_rag](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/chat_rag/chat_rag)

The directory […/chat_rag](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/chat_rag/chat_rag) coordinates an end-to-end workflow for conversational modeling involving information retrieval and response generation. The /__init__.py file handles the overall workflow by initializing attributes for various components and calling their methods in a defined order.

The […/data](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/chat_rag/chat_rag/data) subdirectory contains functionality for parsing unstructured documents into structured representations.

The […/inf_retrieval](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/chat_rag/chat_rag/inf_retrieval) subdirectory handles key retrieval tasks. Files contain implementations of embedding models for generating text representations and functions for related tasks.

The […/llms](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/chat_rag/chat_rag/llms) subdirectory provides interfaces to different large language models for response generation. Base classes define generation functionality. Files contain classes interfacing with specific LLMs.

The […/intent_detection](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/chat_rag/chat_rag/intent_detection) subdirectory handles intent detection.

### 7.3 Administrative Interface

References: [admin](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin)

The administrative interface provides a centralized dashboard for monitoring and configuring the ChatFAQ conversational AI platform. Key functionality is implemented across several components and stores.

The […/pages](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/pages) directory contains Vue components that define different pages in the interface.

Layouts are defined in […/layouts](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/layouts) using components.

The […/components](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/components) directory contains modular reusable components. The […/task_history](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/components/task_history) components connect to websockets to monitor and display tasks.

State management is centralized using Pinia stores defined in […/store](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/store). The […/items.js](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/store/items.js) store handles item data and loading states. The […/auth.js](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/store/auth.js) store manages the authentication workflow.

Styles are defined in […/styles](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/admin/assets/styles) using variables, mixins and a standardized structure. Components import these styles to promote consistency. Utilities and middleware complete common tasks.

### 7.4 Command Line Interface

References: [cli/chatfaq_cli](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/cli/chatfaq_cli)

The […/chatfaq_cli](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/cli/chatfaq_cli) directory provides a command line interface (CLI) for interacting with the ChatFAQ knowledge management system. It allows users to manage knowledge objects like intents, knowledge bases, and knowledge items through commands.

The CLI is implemented as a Python application using the Typer framework. Authentication is handled through an object passed via context that makes requests to the API.

Subcommands are defined across modules imported in […/__init__.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/cli/chatfaq_cli/__init__.py). For example, the /data directory contains modules that define commands corresponding to common tasks like creating, listing, updating and deleting through functions. These modules interact with the REST API through the object.

The […/intents.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/cli/chatfaq_cli/data/intents.py) module defines commands for listing intents filtered by a knowledge base with a function. These functions make requests to the API endpoints to perform the operations.

Configuration is handled in the […/config](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/cli/chatfaq_cli/config) directory. The […/__init__.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/cli/chatfaq_cli/helpers/__init__.py) file provides an interface to read and write values to the configuration file through functions.

### 7.5 Embeddable Chat Widget

References: [widget](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget)

The ChatFAQ widget allows embedding an interactive chat interface directly into web pages. It can be initialized either as a JavaScript library or as a custom HTML element.

The main functionality resides in the [widget](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget) directory. Here, the […/Widget.vue](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/components/Widget.vue) component manages the overall chat widget UI and conditionally renders parts like the sidebar, title bar, and message content based on the global Vuex store state. It also handles opening/closing the widget and phone orientation detection.

The core chat interface logic is implemented in […/Chat.vue](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/components/chat/Chat.vue). This component initializes a WebSocket connection to the backend chat service on mount. It defines callbacks to handle incoming and outgoing messages over the socket. A heartbeat is sent every 5 seconds to keep the connection alive. Received messages are added to an array and rendered in message stacks. Scrolling is handled to keep the chat view updated.

State is coordinated with the single source of truth Pinia store defined in […/index.js](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/store/index.js). This store provides getters for retrieving data and mutations for updating state. Data includes conversations, messages, users, and flags like whether responses are waiting.

Reusable UI components are defined under […/generic](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/components/generic). For example, […/Loader.vue](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/components/generic/Loader.vue) defines a loading indicator using only HTML and CSS animations via a keyframe. […/Checkbox.vue](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/components/generic/Checkbox.vue) implements an SVG checkbox that tracks its checked state internally with a ref.

The left sidebar menu is defined in […/LeftMenu.vue](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/components/left-menu/LeftMenu.vue). This imports reusable menu item components from […/items](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/components/left-menu/items), like for deleting chat history. These items interface with the global store and make API requests to perform operations.

Global styles are centralized in […/styles](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/widget/assets/styles). Variables define colors, fonts, and breakpoints, allowing values to be updated in one place. Gradient colors are generated from start/end variables. Specific element colors reference general colors for consistency.

### 7.6 Core Documentation

References: [doc/source/modules](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/doc/source/modules)

The core backend services are implemented in the […/back](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back) directory. This includes the main orchestration class mentioned in […/index.md](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/doc/source/modules/back/index.md) that manages widgets and FSM execution. It handles initialization and provides the main interface.

Models and content are managed through the Django admin interfaces.

