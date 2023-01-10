from django.urls import re_path, path

from riddler.apps.broker.consumers import ExampleBotConsumer, RPCConsumer
from riddler.apps.broker.models.platform_config import PlatformConfig, PlatformTypes
from riddler.utils import is_migrating

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

http_urlpatterns = []


def set_up_platform_urls(_urlpatterns):
    if is_migrating():
        return

    for pb in PlatformConfig.objects.all():
        if pb.platform_type == PlatformTypes.telegram.value:
            _urlpatterns.append(path(
                pb.platform_url_path(),
                pb.platform_http_consumer().as_asgi(),
                name=pb.platform_view_name()
            ))


set_up_platform_urls(http_urlpatterns)
