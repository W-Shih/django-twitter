# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#           tweets api unit tests
#
# =================================================================================================
#    Date      Name                    Description of Change
# 06-Sep-2021  Wayne Shih              Initial create
# 10-Oct-2021  Wayne Shih              React to pylint checks
# 04-Nov-2021  Wayne Shih              React to adding anonymous_client to base class
# 06-Nov-2021  Wayne Shih              Modify some assertEqual to check set instead of list
# 27-Nov-2021  Wayne Shih              Add tests for tweet retrieve api
# $HISTORY$
# =================================================================================================


from rest_framework import status
from rest_framework.test import APIClient

from testing.testcases import TestCase
from tweets.models import Tweet


TWEET_LIST_URL = '/api/tweets/'
TWEET_CREATE_URL = '/api/tweets/'
TWEET_RETRIEVE_URL = '/api/tweets/{}/'


class TweetApiTests(TestCase):

    # <Wayne Shih> 06-Sep-2021
    # This method will be executed before executing each test method
    def setUp(self):
        self.user1 = self.create_user(username='lbj23')
        self.tweets1 = [
            self.create_tweet(self.user1)
            for _ in range(3)
        ]
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

        self.user2 = self.create_user(username='kd35')
        self.tweets2 = [
            self.create_tweet(self.user2)
            for _ in range(2)
        ]

    # <Wayne Shih> 06-Sep-2021
    # The name of each test method must start with 'test_'.
    def test_list_api(self):
        response = self.anonymous_client.get(TWEET_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Missing user_id.')

        response = self.anonymous_client.get(TWEET_LIST_URL, {'user_id': self.user1.id})
        tweets = response.data['tweets']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(isinstance(tweets, list), True)
        self.assertEqual(len(tweets), 3)
        self.assertEqual(
            set(tweets[0].keys()),
            {'id', 'user', 'created_at', 'content'}
        )
        # <Wayne Shih> 06-Sep-2021
        # test order by '-created_at'
        for index in range(len(tweets) - 1):
            self.assertEqual(
                tweets[index]['created_at'] > tweets[index + 1]['created_at'],
                True
            )

        response = self.anonymous_client.get(TWEET_LIST_URL, {'user_id': self.user2.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['tweets']), 2)
        # <Wayne Shih> 06-Sep-2021
        # test order by '-created_at'
        self.assertEqual(response.data['tweets'][0]['id'], self.tweets2[1].id)
        self.assertEqual(response.data['tweets'][1]['id'], self.tweets2[0].id)
        self.assertEqual(
            response.data['tweets'][0]['created_at'] > response.data['tweets'][1]['created_at'],
            True
        )

    def test_create_api(self):
        response = self.anonymous_client.post(TWEET_CREATE_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.user1_client.post(TWEET_CREATE_URL)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')

        response = self.user1_client.post(TWEET_CREATE_URL, {'content': '123'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')

        response = self.user1_client.post(TWEET_CREATE_URL, {
            'content': '1' * 256
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')

        tweets_count = Tweet.objects.count()
        response = self.user1_client.post(TWEET_CREATE_URL, {
            'content': 'I am the King James!'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['id'], self.user1.id)
        self.assertEqual(response.data['content'], 'I am the King James!')
        self.assertEqual(Tweet.objects.count(), tweets_count + 1)
        self.assertEqual(response.data['user'], {
            'id': self.user1.id,
            'username': self.user1.username,
        })
        self.assertEqual(
            set(response.data.keys()),
            {'id', 'user', 'created_at', 'content'}
        )

    def test_retrieve_api(self):
        # Non-existing tweet
        non_existing_tweet_id = -1
        url = TWEET_RETRIEVE_URL.format(non_existing_tweet_id)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Get tweet with 0 comment
        tweet = self.create_tweet(self.user1, 'This is for u!')
        url = TWEET_RETRIEVE_URL.format(tweet.id)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json().keys(),
            {'id', 'user', 'comments', 'created_at', 'content'}
        )
        self.assertEqual(response.json().get('user').keys(), {'id', 'username'})
        self.assertEqual(isinstance(response.json().get('comments'), list), True)
        self.assertEqual(len(response.data['comments']), 0)

        # Get tweet with 3 comments
        self.create_comment(self.user1, tweet, 'Chasing the GOAT!')
        self.create_comment(self.user2, tweet, 'Good for u!')
        self.create_comment(
            self.user2,
            self.create_tweet(self.user2, 'another tweet'),
            'tweet man'
        )
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['comments']), 2)
        self.assertEqual(
            response.json().get('comments')[0].keys(),
            {'id', 'tweet_id', 'user', 'content', 'created_at'}
        )
        self.assertEqual(response.data['comments'][0]['user']['username'], self.user1.username)
        self.assertEqual(response.data['comments'][1]['user']['username'], self.user2.username)
        self.assertEqual(
            response.data['comments'][0]['created_at'] <
            response.data['comments'][1]['created_at'],
            True
        )
