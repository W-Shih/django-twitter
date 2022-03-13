# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#           notification service unit tests
#
# =================================================================================================
#    Date      Name                    Description of Change
# 12-Mar-2021  Wayne Shih              Initial create
# $HISTORY$
# =================================================================================================


from notifications.models import Notification

from inbox.services import NotificationService
from testing.testcases import TestCase


class NotificationServiceTest(TestCase):

    def setUp(self):
        self.lbj23 = self.create_user(username='cavs_lbj23')
        self.kobe24 = self.create_user(username='kobe24')
        self.lbj23_tweet = self.create_tweet(user=self.lbj23, content='This is for u!')

    def test_send_comment_notification(self):
        # Comment on my own tweet, don't dispatch notification in this case
        lbj23_comment = self.create_comment(
            user=self.lbj23,
            tweet=self.lbj23_tweet,
            content='I am GOAT!!',
        )
        NotificationService.send_comment_notification(lbj23_comment)
        self.assertEqual(Notification.objects.count(), 0)

        # dispatch notification if other commented on the tweet
        kobe24_comment = self.create_comment(
            user=self.kobe24,
            tweet=self.lbj23_tweet,
            content='Good job, my bro',
        )
        NotificationService.send_comment_notification(kobe24_comment)
        self.assertEqual(Notification.objects.count(), 1)

    def test_send_like_notification(self):
        # Like on my own tweet, don't dispatch notification in this case
        lbj23_tweet_like = self.create_like(user=self.lbj23, target=self.lbj23_tweet)
        NotificationService.send_like_notification(lbj23_tweet_like)
        self.assertEqual(Notification.objects.count(), 0)

        # dispatch notification if other liked the tweet
        kobe24_tweet_like = self.create_like(user=self.kobe24, target=self.lbj23_tweet)
        NotificationService.send_like_notification(kobe24_tweet_like)
        self.assertEqual(Notification.objects.count(), 1)

        kobe24_comment = self.create_comment(
            user=self.kobe24,
            tweet=self.lbj23_tweet,
            content='Good job, my bro',
        )
        lbj23_comment_like = self.create_like(user=self.lbj23, target=kobe24_comment)
        NotificationService.send_like_notification(lbj23_comment_like)
        self.assertEqual(Notification.objects.count(), 2)
