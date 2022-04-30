# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#           newsfeed api unit tests
#
# =================================================================================================
#    Date      Name                    Description of Change
# 04-Nov-2021  Wayne Shih              Initial create
# 27-Apr-2022  Wayne Shih              Add tests for newfeed list endless pagination
# 29-Apr-2022  Wayne Shih              React to deprecating key in newsfeeds list api
# $HISTORY$
# =================================================================================================


from urllib import parse

from rest_framework import status
from rest_framework.test import APIClient

from testing.testcases import TestCase
from utils.pagination import EndlessPagination


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
        self.assertEqual(len(response.data['results']), 0)

        # test seeing user's own tweet
        self.lbj23_client.post(TWEET_CREATE_URL, {'content': 'I am the King James!'})
        response = self.lbj23_client.get(NEWSFEED_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

        # able to see someone's tweet after following
        self.lbj23_client.post(FOLLOW_URL.format(self.kobe24.id))
        self.kobe24_client.post(TWEET_CREATE_URL, {'content': 'Be Better!'})
        response = self.lbj23_client.get(NEWSFEED_LIST_URL)
        newsfeeds = response.data['results']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(newsfeeds), 2)
        self.assertEqual(newsfeeds[0]['created_at'] > newsfeeds[1]['created_at'], True)

    def test_list_pagination(self):
        page_size = EndlessPagination.page_size

        newsfeeds = []
        num_newsfeeds = page_size * 2 - 1
        for i in range(num_newsfeeds):
            tweet = self.create_tweet(self.kobe24, f'kb24::tweet::{i}')
            newsfeed = self.create_newsfeed(self.lbj23, tweet)
            newsfeeds.append(newsfeed)
        newsfeeds = newsfeeds[::-1]

        # Test the first page of lbj23's newsfeeds  <Wayne Shih> 27-Apr-2022
        response = self.lbj23_client.get(NEWSFEED_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['has_next'], True)
        self.assertEqual(response.data['results'][0]['id'], newsfeeds[0].id)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(
            response.data['results'][page_size - 1]['id'],
            newsfeeds[page_size - 1].id
        )
        self.assertEqual(
            str(newsfeeds[page_size - 1].created_at.time()) in parse.unquote(response.data['next']),
            True
        )
        self.assertEqual(
            str(newsfeeds[page_size - 1].created_at.date()) in parse.unquote(response.data['next']),
            True
        )

        # Test the second/last page of lbj23's newsfeeds  <Wayne Shih> 27-Apr-2022
        response = self.lbj23_client.get(NEWSFEED_LIST_URL, {
            'created_at__lt': newsfeeds[page_size - 1].created_at,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['has_next'], False)
        self.assertEqual(response.data['next'], None)
        self.assertEqual(len(response.data['results']), page_size - 1)
        self.assertEqual(response.data['results'][0]['id'], newsfeeds[page_size].id)
        self.assertEqual(
            response.data['results'][page_size - 2]['id'],
            newsfeeds[page_size * 2 - 2].id
        )

        # Test lbj23's new newsfeeds  <Wayne Shih> 27-Apr-2022
        response = self.lbj23_client.get(NEWSFEED_LIST_URL, {
            'created_at__gt': newsfeeds[0].created_at,
        })
        self.assertEqual(response.data['has_next'], False)
        self.assertEqual(response.data['next'], None)
        self.assertEqual(len(response.data['results']), 0)

        new_tweet1 = self.create_tweet(self.lbj23, 'lbj23::new_tweet::1')
        new_tweet2 = self.create_tweet(self.lbj23, 'lbj23::new_tweet::2')
        new_newsfeed1 = self.create_newsfeed(self.lbj23, new_tweet1)
        new_newsfeed2 = self.create_newsfeed(self.lbj23, new_tweet2)
        response = self.lbj23_client.get(NEWSFEED_LIST_URL, {
            'created_at__gt': newsfeeds[0].created_at,
        })
        self.assertEqual(response.data['has_next'], False)
        self.assertEqual(response.data['next'], None)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['id'], new_newsfeed2.id)
        self.assertEqual(response.data['results'][1]['id'], new_newsfeed1.id)
