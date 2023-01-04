from django.urls import re_path

from riddler.apps.broker.consumers import ExampleBotConsumer, RPCConsumer

websocket_urlpatterns = [
    re_path(
        r"back/ws/broker/rpc/(?P<fsm_id>\w+)/$",
        RPCConsumer.as_asgi(),
    ),
    re_path(
        r"back/ws/broker/rpc/$",
        RPCConsumer.as_asgi(),
    ),
    re_path(
        r"back/ws/broker/(?P<conversation>\w+)/(?P<pc_id>\w+)/$",
        ExampleBotConsumer.as_asgi(),
    ),
]
