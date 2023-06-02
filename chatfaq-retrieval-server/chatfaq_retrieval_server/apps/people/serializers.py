from rest_framework import serializers

from .models import User


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
