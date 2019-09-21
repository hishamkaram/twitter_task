"""Api Views.

This module contains the api endpoints.

"""
from django.conf import settings
from requests.exceptions import ConnectionError
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import TweetSerializer
from .twitter import TwitterApi, TwitterException


@api_view(['GET'])
def get_tweets_by_hashtag(request, hashtag):
    """Endpoint to Get Twitter Tweets By Hashtag.

    Args:
        request (django.http.HttpRequest):
            django request object.
        hashtag (str):
            name of the hashtag.

    Returns:
        HttpReponse with a list of hashtag tweets.

    """
    try:
        api = TwitterApi.init_from_settings()
        default_limit = settings.TWITTER_DEFAULT_LIMIT
        limit = request.GET.get("limit", default_limit)
        limit = int(limit)
        tweets = api.get_hashtag_tweets(hashtag, limit)
        serializer = TweetSerializer(tweets, many=True)
        return Response(serializer.data, status=200)
    except (TwitterException, ConnectionError) as e:
        error_data = {"error": str(e)}
        code = 500
        if isinstance(e, TwitterException):
            code = e.code
        else:
            error_data = {"error": "Failed to connect to twitter api."}
        return Response(error_data, status=code)


@api_view(['GET'])
def get_user_timeline(request, screen_name):
    """Endpoint to Get a list of tweets that the user has on his feed.

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
    try:
        api = TwitterApi.init_from_settings()
        tweets = api.get_user_timeline(screen_name, limit)
        serializer = TweetSerializer(tweets, many=True)
        return Response(serializer.data, status=200)
    except (TwitterException, ConnectionError) as e:
        error_data = {"error": str(e)}
        code = 500
        if isinstance(e, TwitterException):
            code = e.code
        else:
            error_data = {"error": "Failed to connect to twitter api."}
        return Response(error_data, status=code)
