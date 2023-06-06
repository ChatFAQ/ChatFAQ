import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "chatfaq_retrieval_server.config.settings"
)


def make_app(django_app):
    """
    This could contain an import that must happen after Django was initialized,
    that's why it is contained inside a function inside of being top-level

    Parameters
    ----------
    django_app
        Output of get_asgi_application()
    """

    from chatfaq_retrieval_server.config.routing import websocket_urlpatterns

    return ProtocolTypeRouter(
        {
            "http": django_app,
            "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
        }
    )


application = make_app(get_asgi_application())
