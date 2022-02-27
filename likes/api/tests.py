# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#           likes api unit tests
#
# =================================================================================================
#    Date      Name                    Description of Change
# 26-Feb-2021  Wayne Shih              Initial create
# $HISTORY$
# =================================================================================================


from rest_framework import status

from likes.models import Like
from testing.testcases import TestCase


# <Wayne Shih> 06-Nov-2021
# URL MUST end with '/', OW, status_code will become 301
LIKE_BASE_URL = '/api/likes/'


class LikeApiTests(TestCase):

    def setUp(self):
        self.lbj23, self.lbj23_client = self.create_user_and_auth_client(username='lbj23')
        self.lbj23_tweet = self.create_tweet(self.lbj23, 'This is for u!!')

        self.kd35, self.kd35_client = self.create_user_and_auth_client(username='kd35')
        self.kd35_comment = self.create_comment(
            user=self.kd35,
            tweet=self.lbj23_tweet,
            content='Good job, my bro',
        )

    def test_create_likes(self):
        response = self.anonymous_client.post(LIKE_BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.anonymous_client.patch(LIKE_BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.lbj23_client.put(LIKE_BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.lbj23_client.post(LIKE_BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')
        self.assertEqual(
            response.data['errors'],
            'Request is missing param(s): content_type, object_id. '
            'All missing params are required to provide.'
        )

        response = self.lbj23_client.post(LIKE_BASE_URL, {'object_id': self.lbj23_tweet})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')
        self.assertEqual(
            response.data['errors'],
            'Request is missing param(s): content_type. All missing params are required to provide.'
        )

        response = self.lbj23_client.post(LIKE_BASE_URL, {'content_type': 'tweet'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')
        self.assertEqual(
            response.data['errors'],
            'Request is missing param(s): object_id. All missing params are required to provide.'
        )

        non_existing_tweet_id = 0
        response = self.lbj23_client.post(LIKE_BASE_URL, {
            'content_type': 'tweet',
            'object_id': non_existing_tweet_id,
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')
        self.assertEqual(
            response.data['errors']['object_id'][0],
            'Object does not exist.'
        )

        dummy_content_type = 'tweeeeeeeeeeeeeeeeet'
        response = self.lbj23_client.post(LIKE_BASE_URL, {
            'content_type': dummy_content_type,
            'object_id': self.lbj23_tweet.id,
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')
        self.assertEqual(
            response.data['errors']['content_type'][0],
            f'"{dummy_content_type}" is not a valid choice.'
        )

        response = self.lbj23_client.post(LIKE_BASE_URL, {
            'content_type': 'tweet',
            'object_id': self.lbj23_tweet.id,
        })
        likes_count = Like.objects.count()
        created_at = response.data['created_at']
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(set(response.data.keys()), {'user', 'created_at'})
        self.assertEqual(response.data['user'], {
            'id': self.lbj23.id,
            'username': self.lbj23.username,
        })
        self.assertEqual(likes_count, 1)

        response = self.lbj23_client.post(LIKE_BASE_URL, {
            'content_type': 'tweet',
            'object_id': self.lbj23_tweet.id,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Like.objects.count(), likes_count)
        self.assertEqual(response.data['created_at'], created_at)

        response = self.kd35_client.post(LIKE_BASE_URL, {
            'content_type': 'tweet',
            'object_id': self.lbj23_tweet.id,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Like.objects.count(), 2)

        response = self.lbj23_client.post(LIKE_BASE_URL, {
            'content_type': 'comment',
            'object_id': self.kd35_comment.id,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Like.objects.count(), 3)
