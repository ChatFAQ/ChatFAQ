
from django.contrib.auth import authenticate, login, logout
from drf_spectacular.utils import PolymorphicProxySerializer, extend_schema
from knox.views import LoginView as KnoxLoginView
from rest_framework import permissions, viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from .models import User
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from .serializers import AnonUserSerializer, AuthRequest, AuthUserSerializer, AdminUserSerializer, GroupSerializer, \
    PermissionSerializer, ContentTypeSerializer


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


class LoginView(KnoxLoginView):
    authentication_classes = [BasicAuthentication]
    permission_classes = (permissions.AllowAny,)


class UserAPIViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer

    def update(self, request, *args, **kwargs):
        password = request.data.get("password")
        if password:
            user = self.get_object()
            user.set_password(password)
            user.save()
            request.data["password"] = user.password
        return super().update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.set_password(request.data.get("password"))
        user.save()
        serializer.data["password"] = user.password
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class GroupAPIViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class PermissionAPIViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    pagination_class = None


class ContentTypeAPIViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ContentType.objects.all()
    serializer_class = ContentTypeSerializer
    pagination_class = None
