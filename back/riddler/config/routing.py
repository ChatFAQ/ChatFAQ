from django.urls import re_path

from riddler.apps.broker.consumers import RiddlerConsumer

websocket_urlpatterns = [
    re_path(
        r"back/ws/broker/(?P<conversation>\w+)/(?P<pc_id>\w+)/$",
        RiddlerConsumer.as_asgi(),
    ),
]
