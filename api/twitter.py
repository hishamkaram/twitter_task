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
        self.date = self.formate_date(_str_date)
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

    def formate_date(self, date):
        """Accept Date as String in twitter Format and return it in
        ``%-I:%-M %p - %-d %b %Y`` format.

        Args:
            date (str):
                date as string in twitter format.

        Returns:
            date formatted in target format.

        """
        return time.strftime('%-I:%-M %p - %-d %b %Y',
                             self.parse_twitter_date(date))


class TwitterApi(object):
    """A python interface into communicate with the Twitter API.

    Example usage:
      To create an instance of the api.twitter.TwitterApi class:
        >>> from api.twitter import TwitterApi
        >>> api = TwitterApi(<api_key>,<api_secret>)
      To fetch a hashtag tweets by hashtag name.
        >>> tweets = api.get_hashtag_tweets(<hashtag_name>)
        >>> print([tweet.text for tweet in tweets])
      To fetch your friends (after being authenticated):
        >>> users = api.GetFriends()
        >>> print([u.name for u in users])
    """

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
        self.get_bearer_token()
        self.set_requests_auth()
        self.session = requests_retry_session()

    def set_requests_auth(self):
        """Set requests auth obj for this instance using the bearer_token ."""
        self.__auth = OAuth2(token=self.bearer_token)

    def get_bearer_token(self):
        """Generate a Bearer Token from twitter api_key and api_secret ."""
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
          requests.Session obj

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
        data = [Tweet(tweet_data) for tweet_data in data['statuses']]
        return data

    # def get_user_timeline(self, username,
    #                       count=settings.TWITTER_DEFAULT_LIMIT):
    #     """Get tweets by a hashtag.

    #     Args:
    #       hashtag (str):
    #         Twitter Hashtag
    #       count (int, optional):
    #         The number of tweets to return per page, up to a maximum of 100.
    #         Defaults to 30.

    #     Returns:
    #       requests.Session obj

    #     """
    #     url = urljoin(self.base_url, "/search/tweets.json")
    #     response = self.session.get(
    #         url,
    #         params={
    #             "q": hashtag,
    #             "count": count,
    #             "include_entities": True
    #         },
    #         auth=self.__auth,
    #     )
    #     return response.json()


twitter_api = TwitterApi(settings.TWITTER_API_KEY, settings.TWITTER_API_SECRET)
