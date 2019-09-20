"""Api Views.

This module contains the api endpoints.

"""
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import TweetSerializer
from .twitter import twitter_api


@api_view(['GET'])
def get_tweets_by_hashtag(request, hashtag):
    """Api Endpoint to Get Twitter Tweets By Hashtag.

    Args:
        request (django.http.HttpRequest):
            django request object.
        hashtag (str):
            name of the hashtag.

    Returns:
        HttpReponse with a list of hashtag tweets.

    """
    default_limit = settings.TWITTER_DEFAULT_LIMIT
    limit = request.GET.get("limit", default_limit)
    limit = int(limit)
    tweets = twitter_api.get_hashtag_tweets(hashtag, limit)
    serializer = TweetSerializer(tweets, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_user_timeline(request, screen_name):
    """Api Endpoint to Get a list of tweets that the user has on his feed.

    Args:
        request (django.http.HttpRequest):
            django request object.
        screen_name (str):
            Twitter screen_name or username of the user.

    Returns:
        HttpReponse with a list of timeline tweets.

    """
    default_limit = settings.TWITTER_DEFAULT_LIMIT
    limit = request.GET.get("limit", default_limit)
    limit = int(limit)
    tweets = twitter_api.get_user_timeline(screen_name, limit)
    serializer = TweetSerializer(tweets, many=True)
    return Response(serializer.data)
