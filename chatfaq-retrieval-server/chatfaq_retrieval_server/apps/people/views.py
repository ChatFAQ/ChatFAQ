from django.contrib.auth import authenticate, login, logout
from drf_spectacular.utils import PolymorphicProxySerializer, extend_schema
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from .serializers import AnonUserSerializer, AuthRequest, AuthUserSerializer


class MeViewSet(viewsets.GenericViewSet):
    """
    Basic ViewSet that handles login and loging of the user through the API
    using the session.
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = AuthUserSerializer
    pagination_class = None

    def get_serializer_class(self):
        if self.action == "create":
            return AuthRequest
        else:
            return AuthUserSerializer

    @extend_schema(
        operation_id="get_current_user",
        responses=PolymorphicProxySerializer(
            component_name="User",
            resource_type_field_name="is_authenticated",
            serializers={
                "true": AuthUserSerializer,
                "false": AnonUserSerializer,
            },
            many=False,
        ),
    )
    def list(self, request: Request) -> Response:
        """
        Retrieves the user's current information, whether they are logged in or
        not.
        """

        if request.user.is_authenticated:
            data = AuthUserSerializer(
                instance=request.user,
                context=self.get_serializer_context(),
            ).data
        else:
            data = dict(is_authenticated=False)

        return Response(data)

    @extend_schema("login")
    def create(self, request: Request) -> Response:
        """
        Call this to login. It will implicitly logout if logged in already.
        """

        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)

        if request.user.is_authenticated:
            logout(request)

        if user := authenticate(request, **ser.validated_data):
            login(request, user)

        return self.list(request)  # noqa

    @extend_schema("logout")
    @action(methods=["post"], detail=False)
    def logout(self, request: Request) -> Response:
        """
        Call this to logout. If already not connected then nothing happens.
        """

        if request.user.is_authenticated:
            logout(request)

        return self.list(request)  # noqa
