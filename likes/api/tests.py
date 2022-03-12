# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#           likes api unit tests
#
# =================================================================================================
#    Date      Name                    Description of Change
# 26-Feb-2022  Wayne Shih              Initial create
# 05-Mar-2022  Wayne Shih              Add tests for like cancel and list APIs
# 12-Mar-2022  Wayne Shih              Add tests for likes in tweets and comments
# $HISTORY$
# =================================================================================================


from rest_framework import status

from likes.models import Like
from testing.testcases import TestCase


# <Wayne Shih> 26-Feb-2022
# URL MUST end with '/', OW, status_code will become 301
DRF_LIKE_API_URL = '/api/likes/'
LIKE_BASE_URL = '/api/likes/'
LIKE_CANCEL_URL = '/api/likes/cancel/'
COMMENT_LIST_URL = '/api/comments/'
TWEET_DETAIL_URL = '/api/tweets/{}/'
TWEET_LIST_URL = '/api/tweets/'
NEWSFEED_LIST_URL = '/api/newsfeeds/'


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

    def test_drf_api_page(self):
        response = self.anonymous_client.get(DRF_LIKE_API_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_likes(self):
        # <Wayne Shih> 05-Mar-2022
        # Login required
        response = self.anonymous_client.post(LIKE_BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.anonymous_client.patch(LIKE_BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # <Wayne Shih> 05-Mar-2022
        # Only post is allowed
        response = self.lbj23_client.put(LIKE_BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # <Wayne Shih> 05-Mar-2022
        # Required input check
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

        # <Wayne Shih> 05-Mar-2022
        # Input is not valid
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

        # <Wayne Shih> 05-Mar-2022
        # lbj23 likes tweet successful
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

        # <Wayne Shih> 05-Mar-2022
        # lbj23 likes the same tweet
        response = self.lbj23_client.post(LIKE_BASE_URL, {
            'content_type': 'tweet',
            'object_id': self.lbj23_tweet.id,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Like.objects.count(), likes_count)
        self.assertEqual(response.data['created_at'], created_at)

        # <Wayne Shih> 05-Mar-2022
        # kd35 likes tweet successful
        response = self.kd35_client.post(LIKE_BASE_URL, {
            'content_type': 'tweet',
            'object_id': self.lbj23_tweet.id,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Like.objects.count(), 2)

        # <Wayne Shih> 05-Mar-2022
        # lbj23 likes comment successful
        response = self.lbj23_client.post(LIKE_BASE_URL, {
            'content_type': 'comment',
            'object_id': self.kd35_comment.id,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Like.objects.count(), 3)

    def test_cancel_like(self):
        self.create_like(self.kd35, self.lbj23_tweet)
        self.create_like(self.lbj23, self.kd35_comment)
        self.assertEqual(self.lbj23_tweet.like_set.count(), 1)
        self.assertEqual(self.kd35_comment.like_set.count(), 1)
        self.assertEqual(Like.objects.count(), 2)

        # <Wayne Shih> 05-Mar-2022
        # Login required
        response = self.anonymous_client.patch(LIKE_CANCEL_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.anonymous_client.post(LIKE_CANCEL_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # <Wayne Shih> 05-Mar-2022
        # Only post is allowed
        response = self.kd35_client.put(LIKE_CANCEL_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # <Wayne Shih> 05-Mar-2022
        # Input is not valid
        wrong_content_type = 'wrong_content_type'
        response = self.lbj23_client.post(LIKE_CANCEL_URL, {
            'content_type': wrong_content_type,
            'object_id': self.kd35_comment,
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')
        self.assertEqual(
            response.data['errors']['content_type'][0],
            f'"{wrong_content_type}" is not a valid choice.'
        )

        non_existing_comment_id = 0
        response = self.lbj23_client.post(LIKE_CANCEL_URL, {
            'content_type': 'comment',
            'object_id': non_existing_comment_id,
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')
        self.assertEqual(
            response.data['errors']['object_id'][0],
            'Object does not exist.'
        )

        # <Wayne Shih> 05-Mar-2022
        # lbj23 didn't like the tweet before
        response = self.lbj23_client.post(LIKE_CANCEL_URL, {
            'content_type': 'tweet',
            'object_id': self.lbj23_tweet.id,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['num_deleted'], 0)
        self.assertEqual(self.lbj23_tweet.like_set.count(), 1)
        self.assertEqual(self.kd35_comment.like_set.count(), 1)
        self.assertEqual(Like.objects.count(), 2)

        # <Wayne Shih> 05-Mar-2022
        # kd35 didn't like the comment before
        response = self.kd35_client.post(LIKE_CANCEL_URL, {
            'content_type': 'comment',
            'object_id': self.kd35_comment.id,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['num_deleted'], 0)
        self.assertEqual(Like.objects.count(), 2)
        self.assertEqual(self.lbj23_tweet.like_set.count(), 1)
        self.assertEqual(self.kd35_comment.like_set.count(), 1)

        # <Wayne Shih> 05-Mar-2022
        # kd35 canceled the tweet like
        response = self.kd35_client.post(LIKE_CANCEL_URL, {
            'content_type': 'tweet',
            'object_id': self.lbj23_tweet.id,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['num_deleted'], 1)
        self.assertEqual(Like.objects.count(), 1)
        self.assertEqual(self.lbj23_tweet.like_set.count(), 0)
        self.assertEqual(self.kd35_comment.like_set.count(), 1)

        # <Wayne Shih> 05-Mar-2022
        # lbj23 re-cancel the comment like
        self.create_like(self.kd35, self.kd35_comment)
        self.assertEqual(Like.objects.count(), 2)
        self.assertEqual(self.kd35_comment.like_set.count(), 2)

        response = self.lbj23_client.post(LIKE_CANCEL_URL, {
            'content_type': 'comment',
            'object_id': self.kd35_comment.id,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['num_deleted'], 1)
        self.assertEqual(Like.objects.count(), 1)
        self.assertEqual(self.kd35_comment.like_set.count(), 1)

        response = self.lbj23_client.post(LIKE_CANCEL_URL, {
            'content_type': 'comment',
            'object_id': self.kd35_comment.id,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['num_deleted'], 0)
        self.assertEqual(Like.objects.count(), 1)
        self.assertEqual(self.kd35_comment.like_set.count(), 1)

    def test_likes_in_comments(self):
        # <Wayne Shih> 12-Mar-2022
        # This test is to test likes in CommentSerializer
        #
        # test COMMENT_LIST_URL for a given tweet
        # test anonymous
        response = self.anonymous_client.get(COMMENT_LIST_URL, {
            'tweet_id': self.lbj23_tweet.id
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['comments'][0]['likes_count'], 0)
        self.assertEqual(response.data['comments'][0]['has_liked'], False)

        # test log-in user
        response = self.lbj23_client.get(COMMENT_LIST_URL, {
            'tweet_id': self.lbj23_tweet.id
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['comments'][0]['has_liked'], False)
        self.assertEqual(response.data['comments'][0]['likes_count'], 0)
        self.create_like(self.lbj23, self.kd35_comment)
        response = self.lbj23_client.get(COMMENT_LIST_URL, {
            'tweet_id': self.lbj23_tweet.id
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['comments'][0]['has_liked'], True)
        self.assertEqual(response.data['comments'][0]['likes_count'], 1)

        # test COMMENT_LIST_URL for a given user
        response = self.anonymous_client.get(COMMENT_LIST_URL, {
            'user_id': self.kd35.id
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['comments'][0]['likes_count'], 1)
        self.assertEqual(response.data['comments'][0]['has_liked'], False)

        # test likes in comments for a given TWEET_DETAIL_URL
        self.create_like(self.kd35, self.kd35_comment)
        url = TWEET_DETAIL_URL.format(self.lbj23_tweet.id)
        response = self.lbj23_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['comments'][0]['likes_count'], 2)
        self.assertEqual(response.data['comments'][0]['has_liked'], True)

    def test_likes_in_tweets(self):
        # <Wayne Shih> 12-Mar-2022
        # This test is to test likes in TweetSerializer and TweetSerializerForDetail
        #
        # test TWEET_LIST_URL
        response = self.anonymous_client.get(TWEET_LIST_URL, {
            'user_id': self.lbj23.id
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['tweets'][0]['likes_count'], 0)
        self.assertEqual(response.data['tweets'][0]['has_liked'], False)

        self.create_like(self.lbj23, self.lbj23_tweet)
        response = self.lbj23_client.get(TWEET_LIST_URL, {
            'user_id': self.lbj23.id
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['tweets'][0]['likes_count'], 1)
        self.assertEqual(response.data['tweets'][0]['has_liked'], True)

        # lbj re-liked the same comment
        self.create_like(self.lbj23, self.lbj23_tweet)
        response = self.kd35_client.get(TWEET_LIST_URL, {
            'user_id': self.lbj23.id
        })
        self.assertEqual(response.data['tweets'][0]['likes_count'], 1)
        self.assertEqual(response.data['tweets'][0]['has_liked'], False)

        # test NEWSFEED_LIST_URL
        self.create_like(self.kd35, self.lbj23_tweet)
        self.create_newsfeed(self.kd35, self.lbj23_tweet)
        response = self.kd35_client.get(NEWSFEED_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['newsfeeds'][0]['tweet']['likes_count'], 2)
        self.assertEqual(response.data['newsfeeds'][0]['tweet']['has_liked'], True)

        # test likes and their detail in tweet detail
        url = TWEET_DETAIL_URL.format(self.lbj23_tweet.id)
        response = self.lbj23_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['has_liked'], True)
        self.assertEqual(response.data['likes_count'], 2)
        self.assertEqual(len(response.data['likes']), 2)
        self.assertEqual(response.data['likes'][0]['user']['id'], self.kd35.id)
        self.assertEqual(response.data['likes'][1]['user']['id'], self.lbj23.id)
