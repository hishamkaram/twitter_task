import base64

import requests
from django.conf import settings
from requests.utils import quote
from requests_oauthlib import OAuth2

from .utils import requests_retry_session, urljoin


class TwitterApi(object):
    def __init__(self, api_key, api_secret, base_url=settings.TWITTER_API_URL):
        """Instantiate a new api.twitter.TwitterApi object.

        Args:
          api_key (str):
            Twitter API key
          api_secret (str):
            Twitter API secret
          base_url (str, optional):
            The base URL to use to communicate with the Twitter API.
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
        return response.json()
