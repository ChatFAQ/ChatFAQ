import fnmatch
from logging import getLogger
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from django.contrib.auth import authenticate
from knox.auth import TokenAuthentication
from rest_framework import exceptions

from rest_framework.permissions import BasePermission

from back.apps.widget.models import Widget
from urllib.parse import urlparse

from functools import wraps
from asgiref.sync import sync_to_async
from knox.auth import TokenAuthentication
from django.http import JsonResponse

logger = getLogger(__name__)


@database_sync_to_async
def return_user_from_token(token_string):
    from django.contrib.auth.models import AnonymousUser
    from rest_framework.authtoken.models import Token

    try:
        user = Token.objects.get(key=token_string).user
    except Token.DoesNotExist:
        user = AnonymousUser()
    return user


@database_sync_to_async
def return_user_from_knox_token(token_string=""):
    from django.contrib.auth.models import AnonymousUser

    try:
        user, auth_token = TokenAuthentication().authenticate_credentials(
            token_string.encode()
        )
    except exceptions.AuthenticationFailed as e:
        user = AnonymousUser()
    return user


@database_sync_to_async
def return_user_from_passw(email, passw):
    from django.contrib.auth.models import AnonymousUser

    user = authenticate(email=email, password=passw)
    if user is None:
        user = AnonymousUser()
    return user


class TokenAuthMiddleWare:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        token = parse_qs(scope["query_string"].decode()).get("token")
        token = token[0] if token else ""
        user = await return_user_from_knox_token(token)
        scope["user"] = user
        return await self.app(scope, receive, send)


class PassAuthMiddleWare:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        email = parse_qs(scope["query_string"].decode()).get("email")
        passw = parse_qs(scope["query_string"].decode()).get("pass")
        email = email[0] if email else None
        passw = passw[0] if passw else None
        user = await return_user_from_passw(email, passw)
        scope["user"] = user
        return await self.app(scope, receive, send)


class IsAuthenticatedOrWidgetOriginHostPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            return True

        origin = request.META.get('HTTP_REFERER')
        widget_id = request.META.get('HTTP_WIDGET_ID')
        try:
            widget = Widget.objects.get(id=widget_id)
        except Widget.DoesNotExist:
            return False
        # Compare netloc to netloc (both should be like "localhost:3000")
        widget_domain_netloc = urlparse(widget.domain).netloc if widget.domain else widget.domain
        if fnmatch.fnmatch(urlparse(origin).netloc, widget_domain_netloc):
            return True
        return False

class KnoxAsyncAuthMixin:
    """Mixin to add Knox authentication to async class-based views."""

    async def dispatch(self, request, *args, **kwargs):
        knox_auth = TokenAuthentication()

        async def authenticate_async():
            try:
                return await sync_to_async(knox_auth.authenticate)(request)
            except Exception as e:
                return None

        auth_result = await authenticate_async()

        if auth_result:
            request.user = auth_result[0]
            request.auth = auth_result[1]
            return await super().dispatch(request, *args, **kwargs)
        else:
            return JsonResponse({"error": "Authentication failed"}, status=401)
