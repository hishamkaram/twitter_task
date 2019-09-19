from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import TweetSerializer
from .twitter import twitter_api


@api_view(['GET'])
def get_tweets_by_hashtag(request, hashtag=None):
    """Get Twitter Tweets By Hashtag.

    Args:
        request (django.http.HttpRequest):
            django request object.
        hashtag (str):
            name of the hashtag.

    Returns:
        HttpReponse with list of hashtag tweets.

    """
    default_limit = settings.TWITTER_DEFAULT_LIMIT
    limit = request.GET.get("limit", default_limit)
    limit = int(limit)
    tweets = twitter_api.get_hashtag_tweets(hashtag, limit)
    serializer = TweetSerializer(tweets, many=True)
    return Response(serializer.data)
