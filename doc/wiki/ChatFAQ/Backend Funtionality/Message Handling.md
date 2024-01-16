### Message Handling

The main functionality for handling incoming messages is implemented in the […/consumers](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/apps/broker/consumers) directory. This directory contains classes that handle receiving messages from various sources and routing them to the appropriate bot logic.

The […/bots](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/apps/broker/consumers/bots) subdirectory contains consumer classes for different platforms.

Handlers in […/__init__.py](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/apps/broker/models/__init__.py) validate incoming data and set associations in the database to route future messages.

The serializers in […/messages](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/apps/broker/serializers/messages) convert payloads between external formats and the internal MML format, allowing different sources to be integrated consistently. Subclasses select the correct serializer.

References: [back/back/apps/broker](https://github.com/ChatFAQ/ChatFAQ/blob/c3fcd5af7a32132802da6bbcdb6321c345a9cc8e/back/back/apps/broker)
