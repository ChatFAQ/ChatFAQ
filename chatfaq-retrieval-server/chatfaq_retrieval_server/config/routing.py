from django.urls import re_path

from chatfaq_retrieval_server.apps.realtime.consumers import PassiveAggressiveConsumer

websocket_urlpatterns = [
    re_path(r"back/ws/hello/$", PassiveAggressiveConsumer.as_asgi()),
]
