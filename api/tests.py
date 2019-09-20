from django.test import TestCase
from api.twitter import TwitterApi, Account, Tweet, TwitterException
from django.conf import settings


class TwitterApiTestCase(TestCase):
    def setUp(self):
        key = settings.TWITTER_API_KEY
        secret = settings.TWITTER_API_SECRET
        self.twitter_api = TwitterApi(key, secret)
        self.hashtag = "#nyc"
        self.hashtag_failure = "!!!!"
        self.screen_name = "AnyMindGroup"
        self.screen_name_failure = "dummy_twitter"

    def test_get_hashtag_tweets(self):
        """Test get_hashtag_tweets success."""
        hashtag_tweets = self.twitter_api.get_hashtag_tweets(self.hashtag)
        count = len(hashtag_tweets)
        self.assertNotEqual(count, 0)
        self.assertLessEqual(count, settings.TWITTER_DEFAULT_LIMIT)
        for tweet in hashtag_tweets:
            self.assertIsInstance(tweet, Tweet)
            self.assertIsInstance(tweet.account, Account)

    def test_get_hashtag_tweets_failure(self):
        """Test get_hashtag_tweets failure."""
        with self.assertRaises(TwitterException):
            self.twitter_api.get_hashtag_tweets(self.hashtag_failure)

    def test_get_user_timeline(self):
        """Test get_user_timeline success."""
        user_tweets = self.twitter_api.get_user_timeline(self.screen_name)
        count = len(user_tweets)
        self.assertNotEqual(count, 0)
        self.assertLessEqual(count, settings.TWITTER_DEFAULT_LIMIT)
        for tweet in user_tweets:
            self.assertIsInstance(tweet, Tweet)
            self.assertIsInstance(tweet.account, Account)

    def test_get_user_timeline_failure(self):
        """Test get_hashtag_tweets failure."""
        with self.assertRaises(TwitterException):
            self.twitter_api.get_user_timeline(self.hashtag_failure)
