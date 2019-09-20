from django.conf import settings
from django.shortcuts import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from api.twitter import Account, Tweet, TwitterApi, TwitterException


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


class ApiTestCase(APITestCase):
    def setUp(self):
        self.hashtag = "#nyc"
        self.hashtag_failure = "!!!!"
        self.screen_name = "AnyMindGroup"
        self.screen_name_failure = "dummy_twitter"

    def test_get_tweets_by_hashtag_view(self):
        """Test get_tweets_by_hashtag view success."""
        url = reverse('tweets-hashtag', kwargs={"hashtag": self.hashtag})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data), settings.TWITTER_DEFAULT_LIMIT)
        response = self.client.get(url, format='json', data={'limit': 50})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data), 50)

    def test_get_user_timeline_view_success(self):
        """Test get_user_timeline view success."""
        url = reverse('user-timeline', kwargs={"screen_name": self.screen_name})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data), settings.TWITTER_DEFAULT_LIMIT)
        response = self.client.get(url, format='json', data={'limit': 50})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data), 50)

    def test_get_user_timeline_view_failure(self):
        """Test get_user_timeline view failure."""
        url = reverse('user-timeline', kwargs={"screen_name": self.screen_name_failure})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)
