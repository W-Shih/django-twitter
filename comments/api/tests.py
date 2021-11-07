# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#           comments api unit tests
#
# =================================================================================================
#    Date      Name                    Description of Change
# 06-Nov-2021  Wayne Shih              Initial create
# $HISTORY$
# =================================================================================================


from rest_framework import status
from rest_framework.test import APIClient

from testing.testcases import TestCase

# <Wayne Shih> 06-Nov-2021
# URL MUST end with '/', OW, status_code will become 301
COMMENT_CREATE_URL = '/api/comments/'


class CommentApiTests(TestCase):

    def setUp(self):
        self.lbj23 = self.create_user(username='lbj23')
        self.lbj23_client = APIClient()
        self.tweet = self.create_tweet(self.lbj23, 'This is for u!!')

        self.kd35 = self.create_user(username='kd35')
        self.kd35_client = APIClient()
        self.kd35_client.force_authenticate(self.kd35)

    def test_create_api(self):
        response = self.anonymous_client.get(COMMENT_CREATE_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.anonymous_client.post(COMMENT_CREATE_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.kd35_client.get(COMMENT_CREATE_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.kd35_client.post(COMMENT_CREATE_URL)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')
        self.assertEqual(
            response.data['errors']['tweet_id'][0],
            'This field may not be null.'
        )
        self.assertEqual(
            response.data['errors']['content'][0],
            'This field may not be null.'
        )

        response = self.kd35_client.post(COMMENT_CREATE_URL, {'tweet_id': self.tweet.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')
        self.assertEqual(
            response.data['errors']['content'][0],
            'This field may not be null.'
        )

        response = self.kd35_client.post(COMMENT_CREATE_URL, {'content': 'Good 4 u, my bro!'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')
        self.assertEqual(
            response.data['errors']['tweet_id'][0],
            'This field may not be null.'
        )

        response = self.kd35_client.post(COMMENT_CREATE_URL, {
            'tweet_id': self.tweet.id,
            'content': '1' * 141
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')
        self.assertEqual('content' in response.data['errors'], True)

        response = self.kd35_client.post(COMMENT_CREATE_URL, {
            'tweet_id': self.tweet.id,
            'content': 'Good 4 u, my bro!'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user'], {
            'id': self.kd35.id,
            'username': self.kd35.username,
        })
        self.assertEqual(response.data['tweet_id'], self.tweet.id)
        self.assertEqual(response.data['content'], 'Good 4 u, my bro!')
        self.assertEqual(
            set(response.data.keys()),
            {'id', 'tweet_id', 'user', 'created_at', 'content'}
        )

        non_existing_tweet_id = 1000
        response = self.kd35_client.post(COMMENT_CREATE_URL, {
            'tweet_id': non_existing_tweet_id,
            'content': 'Good 4 u, my bro!'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')
        self.assertEqual(
            response.data['errors']['tweet_id'][0],
            'tweet does not exist.'
        )
