"""Twitter Api Handler.

This module allow you Connect to twitter api and fetch some useful data from.

    Example usage:
      To create an instance of the api.twitter.TwitterApi class:
        >>> from api.twitter import TwitterApi
        >>> api = TwitterApi(<api_key>,<api_secret>)
      To fetch a hashtag tweets by hashtag name.
        >>> tweets = api.get_hashtag_tweets(<hashtag_name>)
        >>> print([tweet.text for tweet in tweets])
      To fetch tweets on user timeline:
        >>> user_tweets = api.get_user_timeline(<user_screen_name>)
        >>> print([ut.text for ut in user_tweets])
      To fetch tweets on user timeline with limit:
        >>> user_tweets = api.get_user_timeline(<user_screen_name>,<count>)
        >>> print([ut.text for ut in user_tweets])

"""
import base64
import time

import requests
from django.conf import settings
from requests.utils import quote
from requests_oauthlib import OAuth2

from .utils import requests_retry_session, urljoin


class Account:
    """A Python Class which represent a twitter User Account.

    Example usage:
      First create an instance of the api.twitter.Account class:
        >>> from api.serializers import Account
        >>> account=Account(<twitter_api_user_data>)
        >>> account.id
        >>> account.fullname
    """

    def __init__(self, userdata):
        """Instantiate a new api.serializers.Account object.

        Args:
          userdata (dict):
            twitter api user object.

        """
        self.fullname = userdata['name']
        self.href = "/%s" % (userdata['screen_name'])
        self.id = userdata['id']


class Tweet:
    """A Python Class which represent a single tweet.

    Example usage:
      First create an instance of the api.twitter.Tweet class:
        >>> from api.serializers import Tweet
        >>> tweet=Tweet(<twitter_api_tweet_data>)
        >>> tweet.text
    """

    def __init__(self, tweet_data):
        """Instantiate a new api.serializers.Tweet object.

        Args:
          tweet_data (dict):
            twitter api tweet object.

        """
        _hashtags = tweet_data['entities']['hashtags']
        _str_date = tweet_data['created_at']
        self.account = Account(tweet_data['user'])
        self.date = self.format_date(_str_date)
        self.hashtags = ["#%s" % (tag['text']) for tag in _hashtags]
        self.likes = tweet_data['favorite_count']
        # Note: replies number is only available with
        # the Premium and Enterprise tier products.
        # https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/tweet-object # noqa
        self.replies = 0
        self.retweets = tweet_data['retweet_count']
        self.text = tweet_data['text']

    def parse_twitter_date(self, date):
        """Convert string Date to python datetime object.

        Args:
            date (str):
                date as string in twitter format.

        Returns:
            datetime object.

        """
        return time.strptime(date, '%a %b %d %H:%M:%S +0000 %Y')

    def format_date(self, date):
        """Accept Date as string in twitter format and return it in human format.

        Args:
            date (str):
                date as string in twitter format.

        Returns:
            formatted date in more readable format.

        """
        return time.strftime('%-I:%-M %p - %-d %b %Y',
                             self.parse_twitter_date(date))


class TwitterApi(object):
    """A python interface into communicate with the Twitter API."""

    _django_cached_obj = None

    def __init__(self, api_key, api_secret, base_url=settings.TWITTER_API_URL):
        """Instantiate a new api.twitter.TwitterApi object.

        Args:
          api_key (str):
            Twitter API key.

          api_secret (str):
            Twitter API secret.

          base_url (str, optional):
            The base URL to use to communicate with the Twitter API,
            Defaults to https://api.twitter.com/1.1.

        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        self.bearer_token = None
        self.__auth = None
        self.get_bearer_token()
        self.set_requests_auth()
        self.session = requests_retry_session()

    def set_requests_auth(self):
        """Set requests auth obj for this instance using the bearer_token ."""
        self.__auth = OAuth2(token=self.bearer_token)

    def get_bearer_token(self):
        """Generate a Bearer Token from twitter api_key and api_secret .

        Raises:
            requests.exceptions.ConnectionError: if failed to connect to twitter.

        """
        key = quote(self.api_key)
        secret = quote(self.api_secret)
        bearer_token = base64.b64encode("{}:{}".format(key,
                                                       secret).encode("utf8"))

        post_headers = {
            "Authorization": "Basic {0}".format(bearer_token.decode("utf8")),
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        }
        response = requests.post(
            url="https://api.twitter.com/oauth2/token",
            data={"grant_type": "client_credentials"},
            headers=post_headers,
        )
        token_info = response.json()
        self.bearer_token = token_info

    def get_hashtag_tweets(self, hashtag,
                           count=settings.TWITTER_DEFAULT_LIMIT):
        """Get tweets by a hashtag.

        Args:
          hashtag (str):
            Twitter Hashtag
          count (int, optional):
            The number of tweets to return per page, up to a maximum of 100.
            Defaults to 30.

        Returns:
          list of hashtag tweets

        Raises:
            TwitterException: if twitter api returned an error.

        """
        url = urljoin(self.base_url, "/search/tweets.json")
        response = self.session.get(
            url,
            params={
                "q": hashtag,
                "count": count,
                "include_entities": True
            },
            auth=self.__auth,
        )
        data = response.json()
        if response.ok:
            data = [Tweet(tweet_data) for tweet_data in data['statuses']]
        else:
            if 'error' in data:
                raise TwitterException(data['error'], code=response.status_code)
            elif 'errors' in data:
                error = data['errors'][0]
                raise TwitterException(error['message'], code=response.status_code)
        return data

    def get_user_timeline(self, username,
                          count=settings.TWITTER_DEFAULT_LIMIT):
        """Get the list of tweets that the user has on his feed.

        Args:
          username (str):
            Twitter screen_name, username.
          count (int, optional):
            The number of tweets to return per page, up to a maximum of 100.
            Defaults to 30.

        Returns:
          list of tweets that the user has on his feed.

        """
        url = urljoin(self.base_url, "/statuses/user_timeline.json")
        response = self.session.get(
            url,
            params={
                "screen_name": username,
                "count": count,
                # "include_entities": True
            },
            auth=self.__auth,
        )
        data = response.json()
        if response.ok:
            data = [Tweet(tweet_data) for tweet_data in data]
        else:
            if 'error' in data:
                raise TwitterException(data['error'], code=response.status_code)
            elif 'errors' in data:
                error = data['errors'][0]
                raise TwitterException(error['message'], code=response.status_code)
        return data

    @classmethod
    def init_from_settings(cls):
        """Instantiate api.twitter.TwitterApi instance with twitter app_key and app_secret from django settings.

        Returns:
            instance of api.twitter.TwitterApi.

        Raises:
            requests.exceptions.ConnectionError: if failed to connect to twitter.

        """
        if cls._django_cached_obj:
            return cls._django_cached_obj
        api_obj = cls(settings.TWITTER_API_KEY, settings.TWITTER_API_SECRET)
        cls._django_cached_obj = api_obj
        return api_obj


class TwitterException(Exception):
    """A Python class which inherit from Exception used to fire exception when an error occurred."""

    def __init__(self, message, code, *args):
        """Instantiate a new api.twitter.TwitterException object.

        Args:
          message (str):
            Twitter API error message.

          code (str):
            Twitter API status code.

          *args (iteable): arguments passed to the base class.

        """
        self.message = message
        self.code = code
        super(TwitterException, self).__init__(message, code, *args)

    def __str__(self):
        """Representation of the error."""
        return self.message
