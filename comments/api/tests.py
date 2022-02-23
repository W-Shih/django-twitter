# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#           comments api unit tests
#
# =================================================================================================
#    Date      Name                    Description of Change
# 06-Nov-2021  Wayne Shih              Initial create
# 13-Nov-2021  Wayne Shih              Add tests for comments update and destroy apis
# 25-Nov-2021  Wayne Shih              Add tests for comments list api
# 25-Nov-2021  Wayne Shih              Add more tests for comments list api
# 25-Nov-2021  Wayne Shih              Add more tests for comments list api
# 23-Feb-2022  Wayne Shih              React to enhancement by django-filters: filterset_class
# $HISTORY$
# =================================================================================================


from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from comments.models import Comment
from testing.testcases import TestCase

# <Wayne Shih> 06-Nov-2021
# URL MUST end with '/', OW, status_code will become 301
COMMENT_URL = '/api/comments/'
COMMENT_DETAIL_URL = '/api/comments/{}/'


class CommentApiTests(TestCase):

    def setUp(self):
        self.lbj23 = self.create_user(username='lbj23')
        self.lbj23_client = APIClient()
        self.tweet = self.create_tweet(self.lbj23, 'This is for u!!')

        self.kd35 = self.create_user(username='kd35')
        self.kd35_client = APIClient()
        self.kd35_client.force_authenticate(self.kd35)

    def test_create_api(self):
        response = self.anonymous_client.patch(COMMENT_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.anonymous_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.kd35_client.patch(COMMENT_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.kd35_client.post(COMMENT_URL)
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

        response = self.kd35_client.post(COMMENT_URL, {'tweet_id': self.tweet.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')
        self.assertEqual(
            response.data['errors']['content'][0],
            'This field may not be null.'
        )

        response = self.kd35_client.post(COMMENT_URL, {'content': 'Good 4 u, my bro!'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')
        self.assertEqual(
            response.data['errors']['tweet_id'][0],
            'This field may not be null.'
        )

        response = self.kd35_client.post(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'content': '1' * 141
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')
        self.assertEqual('content' in response.data['errors'], True)

        response = self.kd35_client.post(COMMENT_URL, {
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
        response = self.kd35_client.post(COMMENT_URL, {
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

    def test_update_api(self):
        comment = self.create_comment(self.lbj23, self.tweet, 'GOAT!')
        url = COMMENT_DETAIL_URL.format(comment.id)

        # Non-login users
        response = self.anonymous_client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.anonymous_client.put(url, {'content': 'dummy comment'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Not PUT method
        # <Wayne Shih> 13-Nov-2021
        # TODO:
        #   This check might be not not suitable when retrieve api is considered.
        response = self.kd35_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Not comment owner
        response = self.kd35_client.put(url, {'content': 'dummy comment'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Comment owner, but not passing 'content'
        self.lbj23_client.force_authenticate(self.lbj23)
        response = self.lbj23_client.put(url, {'foo_key': 'foo_value'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')
        self.assertEqual(
            response.data['errors']['content'][0],
            'This field may not be null.'
        )

        # Comment owner, update comment successfully
        # <Wayne Shih> 13-Nov-2021
        # Make sure comment object is the latest from db, not from cache
        comment.refresh_from_db()
        new_comment = 'I am chasing the GOAT!'
        self.assertNotEqual(comment.content, new_comment)
        old_comment_id = comment.id
        old_updated_at = comment.updated_at
        old_created_at = comment.created_at

        now = timezone.now()
        another_tweet = self.create_tweet(self.kd35)
        # <Wayne Shih> 13-Nov-2021
        # The update api only allows to update 'content' field as a white list.
        # Test if try to update fields other than 'content'.
        response = self.lbj23_client.put(url, {
            'content': new_comment,
            'user_id': self.kd35.id,
            'tweet_id': another_tweet.id,
            'created_at': now,
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data.keys()),
            {'id', 'tweet_id', 'user', 'created_at', 'content'}
        )
        # <Wayne Shih> 13-Nov-2021
        # Make sure comment object is the latest from db, not from cache
        comment.refresh_from_db()
        self.assertEqual(response.data['id'], old_comment_id)
        self.assertEqual(response.data['tweet_id'], self.tweet.id)
        self.assertEqual(response.data['user'], {
            'id': self.lbj23.id,
            'username': self.lbj23.username,
        })
        self.assertEqual(response.data['content'], new_comment)
        self.assertEqual(comment.created_at, old_created_at)
        self.assertNotEqual(comment.created_at, now)
        self.assertNotEqual(comment.updated_at, old_updated_at)

    def test_delete_api(self):
        comment = self.create_comment(self.lbj23, self.tweet, 'GOAT!')
        url = COMMENT_DETAIL_URL.format(comment.id)

        # Non-login users
        response = self.anonymous_client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.anonymous_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Not DELETE method
        # <Wayne Shih> 13-Nov-2021
        # TODO:
        #   This check might be not not suitable when retrieve api is considered.
        response = self.kd35_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Not comment owner
        response = self.kd35_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Comment owner
        count = Comment.objects.count()
        self.lbj23_client.force_authenticate(self.lbj23)
        response = self.lbj23_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(Comment.objects.count(), count - 1)

    def test_list_api(self):
        response = self.anonymous_client.get(COMMENT_URL)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Non-existing tweet id
        non_existing_tweet_id = -1
        response = self.anonymous_client.get(COMMENT_URL, {
            'tweet_id': non_existing_tweet_id
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['comments']), 0)

        # Non-existing user id
        non_existing_user_id = -1
        response = self.anonymous_client.get(COMMENT_URL, {
            'user_id': non_existing_user_id
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['comments']), 0)

        # No comments on a tweet
        response = self.anonymous_client.get(COMMENT_URL, {
            'tweet_id': self.tweet.id
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['comments']), 0)

        # get comments on a tweet order by 'created_at'
        self.create_comment(self.lbj23, self.tweet, 'I am chasing the GOAT!')
        self.create_comment(self.kd35, self.tweet, 'Good work, bro!')
        self.create_comment(
            self.kd35,
            self.create_tweet(self.kd35, 'another tweet'),
            'how u doing'
        )
        response = self.anonymous_client.get(COMMENT_URL, {
            'tweet_id': self.tweet.id
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['comments']), 2)
        self.assertEqual(
            response.data['comments'][0]['created_at'] <
            response.data['comments'][1]['created_at'],
            True
        )

        # get comments on a tweet filtered by user_id
        response = self.anonymous_client.get(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'user_id': self.lbj23.id,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['comments'][0]['user']['username'], self.lbj23.username)
        self.assertEqual(len(response.data['comments']), 1)

        # get a user's all comments order by 'created_at'
        response = self.anonymous_client.get(COMMENT_URL, {
            'user_id': self.kd35.id,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['comments'][0]['user']['username'], self.kd35.username)
        self.assertEqual(response.data['comments'][1]['user']['username'], self.kd35.username)
        self.assertEqual(len(response.data['comments']), 2)
        self.assertEqual(
            response.data['comments'][0]['created_at'] <
            response.data['comments'][1]['created_at'],
            True
        )

        # foo filter should not affect the result
        response = self.anonymous_client.get(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'foo': self.lbj23.id,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['comments']), 2)
