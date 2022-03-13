# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#           notifications api unit tests
#
# =================================================================================================
#    Date      Name                    Description of Change
# 12-Mar-2022  Wayne Shih              Initial create
# $HISTORY$
# =================================================================================================


from rest_framework import status

from notifications.models import Notification
from testing.testcases import TestCase


# <Wayne Shih> 26-Feb-2022
# URL MUST end with '/', OW, status_code will become 301
COMMENT_BASE_URL = '/api/comments/'
LIKE_BASE_URL = '/api/likes/'


class NotificationApiTests(TestCase):

    def setUp(self):
        self.lbj23, self.lbj23_client = self.create_user_and_auth_client(username='lbj23')
        self.kd35, self.kd35_client = self.create_user_and_auth_client(username='kd35')
        self.lbj23_tweet = self.create_tweet(self.lbj23, 'This is for u!!')

    def test_comment_create_api_triggers_notification(self):
        self.assertEqual(Notification.objects.count(), 0)
        response = self.kd35_client.post(COMMENT_BASE_URL, {
            'tweet_id': self.lbj23_tweet.id,
            'content': 'Good job, my bro! I am going to Worries BTW'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Notification.objects.count(), 1)

    def test_like_create_api_triggers_notification(self):
        self.assertEqual(Notification.objects.count(), 0)
        response = self.kd35_client.post(LIKE_BASE_URL, {
            'content_type': 'tweet',
            'object_id': self.lbj23_tweet.id,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Notification.objects.count(), 1)

        self.kd35_comment = self.create_comment(
            user=self.kd35,
            tweet=self.lbj23_tweet,
            content='Good job, my bro',
        )
        response = self.lbj23_client.post(LIKE_BASE_URL, {
            'content_type': 'comment',
            'object_id': self.kd35_comment.id,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Notification.objects.count(), 2)
