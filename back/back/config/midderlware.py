from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token


@database_sync_to_async
def return_user_from_token(token_string):
    try:
        user = Token.objects.get(key=token_string).user
    except Token.DoesNotExist:
        user = AnonymousUser()
    return user


@database_sync_to_async
def return_user_from_passw(email, passw):
    user = authenticate(email=email, password=passw)
    if user is None:
        user = AnonymousUser()
    return user


class TokenAuthMiddleWare:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        token = parse_qs(scope["query_string"].decode()).get("token")
        token = token[0] if token else None
        user = await return_user_from_token(token)
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
