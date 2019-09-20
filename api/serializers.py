"""Api Serializers.

This module allow you to convert twitter api response to
    Python Objects/Entities.
You can take a look on the following link to check how to user
    Django Rest Serializers:
    ``https://www.django-rest-framework.org/api-guide/serializers/``

"""
from rest_framework import serializers


class AccountSerializer(serializers.Serializer):
    """A Django Rest Framework Serializer Used to serializer/deserializeUser Account."""

    fullname = serializers.CharField(max_length=50)
    href = serializers.CharField(max_length=30)
    id = serializers.IntegerField()


class TweetSerializer(serializers.Serializer):
    """A Django Rest Framework Serializer Used to serializer/deserialize Tweet."""

    account = AccountSerializer()
    date = serializers.CharField()
    hashtags = serializers.ListField()
    likes = serializers.IntegerField()
    replies = serializers.IntegerField()
    retweets = serializers.IntegerField()
    text = serializers.CharField()
