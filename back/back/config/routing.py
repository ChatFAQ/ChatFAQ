from django.urls import re_path

from back.apps.broker.consumers.rpc_consumer import RPCConsumer
from back.common.abs.bot_consumers import BrokerMetaClass
from back.common.abs.bot_consumers.http import HTTPBotConsumer
from back.common.abs.bot_consumers.ws import WSBotConsumer
from back.utils import is_migrating

websocket_urlpatterns = [
    re_path(
        r"back/ws/broker/rpc/(?P<fsm_id>\w+)/$",
        RPCConsumer.as_asgi(),
    ),
    re_path(
        r"back/ws/broker/rpc/$",
        RPCConsumer.as_asgi(),
    ),
]

http_urlpatterns = []


def set_up_platform_urls(_http_urlpatterns, _ws_urlpatterns):
    if is_migrating():
        return

    for pc in BrokerMetaClass.registry:
        if issubclass(pc, HTTPBotConsumer):
            _http_urlpatterns += list(pc.build_path())
        elif issubclass(pc, WSBotConsumer):
            _ws_urlpatterns += list(pc.build_path())


set_up_platform_urls(http_urlpatterns, websocket_urlpatterns)
