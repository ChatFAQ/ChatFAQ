from rest_framework import serializers

from .models import User
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class AdminUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = "__all__"


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = "__all__"


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = "__all__"


class ContentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        fields = "__all__"


class AuthUserSerializer(serializers.ModelSerializer):
    """
    Serializer used when the user is authenticated on /api/me/
    """

    class Meta:
        model = User
        fields = [
            "is_authenticated",
            "first_name",
            "last_name",
            "email",
        ]

    is_authenticated = serializers.BooleanField()


class AnonUserSerializer(serializers.Serializer):
    """
    The serializer used when the user is not authenticated (it's always
    returning the same thing but it's here for the OpenAPI spec).
    """

    class Meta:
        fields = [
            "is_authenticated",
        ]

    is_authenticated = serializers.BooleanField()

    def update(self, instance, validated_data):
        raise NotImplementedError

    def create(self, validated_data):
        raise NotImplementedError


class AuthRequest(serializers.Serializer):
    """
    Serializer to process requests to login
    """

    class Meta:
        fields = [
            "email",
            "password",
        ]

    email = serializers.EmailField()
    password = serializers.CharField()

    def update(self, instance, validated_data):
        raise NotImplementedError

    def create(self, validated_data):
        raise NotImplementedError
