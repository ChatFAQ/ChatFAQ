Backend Functionality
---------------------

The core backend functionality centers around routing messages between services using the […/broker](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/apps/broker) application. This application handles receiving messages from various sources via subclasses of […/http.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/common/abs/bot_consumers/http.py) and […/ws.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/common/abs/bot_consumers/ws.py), which provide a common interface for HTTP and WebSocket consumers. Messages are modeled using classes like from […/message.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/apps/broker/models/message.py), which represents conversations and the messages within them.

Key components for routing messages include:

*   The /bots subdirectory of […/consumers](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/apps/broker/consumers), which contains classes that handle incoming messages from different platforms. These subclasses abstract away platform details.

*   Classes in files like […/__init__.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/apps/broker/consumers/__init__.py), which contains a class that manages websocket connections and associates them with user IDs.

Finite state machines (FSMs) are implemented in […/fsm](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/apps/fsm) to model conversational flows. Models in […/models.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/apps/fsm/models.py) store FSM definitions and cached conversation states.

The […/common](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/common) directory provides reusable abstractions and components. For example, […/bot_consumers](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/common/abs/bot_consumers) contains base classes like that define a common interface for bot consumers to inherit, focusing their code on application logic. Models, serializers, and viewsets in other files provide a consistent data representation.

References: [back/back](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back)
