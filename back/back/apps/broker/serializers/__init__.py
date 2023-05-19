from rest_framework import serializers
from django.apps import apps


class IdSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=255)


class IdsSerializer(serializers.Serializer):
    ids = serializers.ListSerializer(child=serializers.CharField(max_length=255))


class UserFeedbackSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = apps.get_model('broker', 'UserFeedback')


class AdminReviewSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = apps.get_model('broker', 'AdminReview')


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = apps.get_model('broker', 'Message')
