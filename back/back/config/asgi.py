import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from django.urls import re_path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "back.config.settings")


def make_app(django_app):
    """
    This could contain an import that must happen after Django was initialized,
    that's why it is contained inside a function inside of being top-level

    Parameters
    ----------
    django_app
        Output of get_asgi_application()
    """

    from back.config.middelware import TokenAuthMiddleWare  # noqa B101
    from back.config.routing import http_urlpatterns, websocket_urlpatterns

    return ProtocolTypeRouter(
        {
            "http": AuthMiddlewareStack(
                URLRouter(http_urlpatterns + [re_path(r"", django_app)])
            ),
            "websocket": TokenAuthMiddleWare(
                AllowedHostsOriginValidator(
                    AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
                )
            ),
        }
    )


application = make_app(get_asgi_application())
