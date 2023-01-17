from django.urls import re_path, path

from riddler.apps.broker.consumers.rpc_consumer import RPCConsumer
from riddler.apps.broker.consumers.bot_examples.custom_ws import CustomWSBotConsumer
from riddler.apps.broker.models.platform_config import PlatformConfigMetaClass
from riddler.utils import is_migrating

websocket_urlpatterns = [
    re_path(
        r"back/ws/broker/rpc/(?P<fsm_id>\w+)/$",
        RPCConsumer.as_asgi(),
    ),
    re_path(
        r"back/ws/broker/rpc/$",
        RPCConsumer.as_asgi(),
    )
]

http_urlpatterns = []


def set_up_platform_urls(_http_urlpatterns, _ws_urlpatterns):
    if is_migrating():
        return

    for pc_class in PlatformConfigMetaClass.registry:
        for pc in pc_class.get_queryset().all():
            if pc.is_http:
                _http_urlpatterns.append(pc.build_path())
            elif pc.is_ws:
                _ws_urlpatterns.append(pc.build_path())


set_up_platform_urls(http_urlpatterns, websocket_urlpatterns)
