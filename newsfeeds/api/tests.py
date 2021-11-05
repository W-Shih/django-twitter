# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#           newsfeed api unit tests
#
# =================================================================================================
#    Date      Name                    Description of Change
# 04-Nov-2021  Wayne Shih              Initial create
# $HISTORY$
# =================================================================================================


from rest_framework import status
from rest_framework.test import APIClient

from testing.testcases import TestCase


FOLLOW_URL = '/api/friendships/{}/follow/'
NEWSFEED_LIST_URL = '/api/newsfeeds/'
TWEET_CREATE_URL = '/api/tweets/'


class NewsFeedApiTests(TestCase):

    def setUp(self):
        self.lbj23 = self.create_user('lbj23')
        self.lbj23_client = APIClient()
        self.lbj23_client.force_authenticate(self.lbj23)

        self.kobe24 = self.create_user('kobe24')
        self.kobe24_client = APIClient()
        self.kobe24_client.force_authenticate(self.kobe24)

    def test_list_api(self):
        # test not log-in
        response = self.anonymous_client.get(NEWSFEED_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # test http POST instead of GET
        response = self.lbj23_client.post(NEWSFEED_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # test authenticated user with GET
        response = self.lbj23_client.get(NEWSFEED_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['newsfeeds']), 0)

        # test seeing user's own tweet
        self.lbj23_client.post(TWEET_CREATE_URL, {'content': 'I am the King James!'})
        response = self.lbj23_client.get(NEWSFEED_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['newsfeeds']), 1)

        # able to see someone's tweet after following
        self.lbj23_client.post(FOLLOW_URL.format(self.kobe24.id))
        self.kobe24_client.post(TWEET_CREATE_URL, {'content': 'Be Better!'})
        response = self.lbj23_client.get(NEWSFEED_LIST_URL)
        newsfeeds = response.data['newsfeeds']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(newsfeeds), 2)
        self.assertEqual(newsfeeds[0]['created_at'] > newsfeeds[1]['created_at'], True)
