from django.urls import re_path

from riddler.apps.broker.consumers import ExampleBotConsumer, RPCConsumer
from riddler.common.consumers import TestHttpConsumer

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

http_urlpatterns = [
    re_path(
        r"back/ws/broker/http/$",
        TestHttpConsumer.as_asgi(),
    ),

]
