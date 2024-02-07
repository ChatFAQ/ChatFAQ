
import urllib
from django.utils.crypto import constant_time_compare
from django.middleware.csrf import rotate_token
from django.contrib.auth.signals import user_logged_in
from rest_framework.authentication import BasicAuthentication

from django.contrib.auth import SESSION_KEY, _get_user_session_key, HASH_SESSION_KEY, \
    _get_backends, BACKEND_SESSION_KEY

from back.apps.people.models import User


def rememberme_login(request, user, backend=None):
    """
    Persist a user id and a backend in the request. This way a user doesn't
    have to reauthenticate on every request. Note that data set during
    the anonymous session is retained when the user logs in.
    """
    session_auth_hash = ""
    if user is None:
        user = request.user
    if hasattr(user, "get_session_auth_hash"):
        session_auth_hash = user.get_session_auth_hash()

    if SESSION_KEY in request.session:
        if _get_user_session_key(request) != user.pk or (
            session_auth_hash
            and not constant_time_compare(
                request.session.get(HASH_SESSION_KEY, ""), session_auth_hash
            )
        ):
            # To avoid reusing another user's session, create a new, empty
            # session if the existing session corresponds to a different
            # authenticated user.
            request.session.flush()
    else:
        request.session.cycle_key()

    try:
        backend = backend or user.backend
    except AttributeError:
        backends = _get_backends(return_tuples=True)
        if len(backends) == 1:
            _, backend = backends[0]
        else:
            raise ValueError(
                "You have multiple authentication backends configured and "
                "therefore must provide the `backend` argument or set the "
                "`backend` attribute on the user."
            )
    else:
        if not isinstance(backend, str):
            raise TypeError(
                "backend must be a dotted import path string (got %r)." % backend
            )

    request.session[SESSION_KEY] = user._meta.pk.value_to_string(user)
    request.session[BACKEND_SESSION_KEY] = backend
    request.session[HASH_SESSION_KEY] = session_auth_hash
    request.user = user
    rotate_token(request)
    user_logged_in.send(sender=user.__class__, request=request, user=user)


class BasicRememberMeAuthentication(BasicAuthentication):
    def authenticate(self, request):
        # Check if the user sends a remember me cookie, and loh¡g in with it:
        remember_me = request.COOKIES.get("rememberme")
        if remember_me:
            try:
                remember_me = urllib.parse.unquote_plus(remember_me)
                user = User.objects.get(remember_me=remember_me)
                rememberme_login(request, user)
                return (user, None)
            except User.DoesNotExist:
                pass
        return super().authenticate(request)
