# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#           notifications api unit tests
#
# =================================================================================================
#    Date      Name                    Description of Change
# 12-Mar-2022  Wayne Shih              Initial create
# 17-Mar-2022  Wayne Shih              Add notifications api tests
# 19-Mar-2022  Wayne Shih              Add tests for notifications update api
# 19-Mar-2022  Wayne Shih              React to notifications list api change by ListModelMixin
# 26-May-2022  Wayne Shih              Add clear cache before each test
# $HISTORY$
# =================================================================================================


from rest_framework import status

from notifications.models import Notification
from testing.testcases import TestCase


# <Wayne Shih> 12-Mar-2022
# URL MUST end with '/', OW, status_code will become 301
COMMENT_BASE_URL = '/api/comments/'
LIKE_BASE_URL = '/api/likes/'
NOTIFICATION_BASE_URL = '/api/notifications/'
NOTIFICATION_DETAIL_URL = '/api/notifications/{}/'


class NotificationTests(TestCase):

    def setUp(self):
        self.clear_cache()

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


class NotificationApiTests(TestCase):

    def setUp(self):
        self.lbj23, self.lbj23_client = self.create_user_and_auth_client(username='lbj23')
        self.kd35, self.kd35_client = self.create_user_and_auth_client(username='kd35')
        self.lbj23_tweet = self.create_tweet(self.lbj23, 'This is for u!!')

    def test_list(self):
        # Not log-in  <Wayne Shih> 15-Mar-2022
        response = self.anonymous_client.get(NOTIFICATION_BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Method not allowed  <Wayne Shih> 15-Mar-2022
        response = self.kd35_client.post(NOTIFICATION_BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # login user lbj23 has 0 notifications  <Wayne Shih> 15-Mar-2022
        response = self.lbj23_client.get(NOTIFICATION_BASE_URL)
        self.assertEqual(len(response.data['results']), 0)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # login user lbj23 has 2 notifications  <Wayne Shih> 15-Mar-2022
        self.kd35_client.post(LIKE_BASE_URL, {
            'content_type': 'tweet',
            'object_id': self.lbj23_tweet.id,
        })
        kd35_comment_id = self.kd35_client.post(COMMENT_BASE_URL, {
            'tweet_id': self.lbj23_tweet.id,
            'content': 'Good job, my bro! I am going to Worries BTW'
        }).data['id']

        response = self.lbj23_client.get(NOTIFICATION_BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(
            response.data['results'][0]['timestamp'] >
            response.data['results'][1]['timestamp'],
            True
        )
        self.assertEqual(response.data['results'][0]['unread'], True)
        self.assertEqual(response.data['results'][1]['unread'], True)
        self.assertEqual(response.data['results'][0]['actor']['user']['id'], self.kd35.id)
        self.assertEqual(response.data['results'][1]['actor']['user']['id'], self.kd35.id)
        self.assertEqual(
            'commented on your tweet' in response.data['results'][0]['verb'],
            True
        )
        self.assertEqual(
            'liked on your tweet' in response.data['results'][1]['verb'],
            True
        )
        self.assertEqual(
            response.data['results'][0]['target']['tweet']['id'],
            self.lbj23_tweet.id
        )
        self.assertEqual(
            response.data['results'][1]['target']['tweet']['id'],
            self.lbj23_tweet.id
        )

        # <Wayne Shih> 15-Mar-2022
        # login user lbj23 updates 1 notifications to be read
        #
        # https://docs.djangoproject.com/en/4.0/topics/db/queries/#following-relationships-backward
        # According to the src code and Django backward query,
        #   recipient = models.ForeignKey(
        #       settings.AUTH_USER_MODEL,
        #       blank=False,
        #       related_name='notifications',
        #       on_delete=models.CASCADE
        #   )
        # here lbj23 as a recipient, so we can get all notifications of lbj23 by the related_name.
        # i.e. self.lbj23.notifications in this case.
        # It is the same as self.lbj23.notification_set if no related_name is set-up by default.
        # This is equivalent to
        #   Notification.objects.filter(recipient=self.lbj23)
        notification = self.lbj23.notifications.first()
        notification.unread = False
        notification.save()

        response = self.lbj23_client.get(NOTIFICATION_BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        response = self.lbj23_client.get(NOTIFICATION_BASE_URL, {'unread': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.lbj23_client.get(NOTIFICATION_BASE_URL, {'unread': False})
        self.assertEqual(len(response.data['results']), 1)

        # login user kd35 has 0 notifications  <Wayne Shih> 15-Mar-2022
        response = self.kd35_client.get(NOTIFICATION_BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

        # <Wayne Shih> 15-Mar-2022
        # login user kd35 likes his own comment and
        # still has 0 notifications
        self.kd35_client.post(LIKE_BASE_URL, {
            'content_type': 'comment',
            'object_id': kd35_comment_id,
        })
        response = self.kd35_client.get(NOTIFICATION_BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

        # login user lbj23 likes kd35's comment  <Wayne Shih> 17-Mar-2022
        self.lbj23_client.post(LIKE_BASE_URL, {
            'content_type': 'comment',
            'object_id': kd35_comment_id,
        })
        response = self.kd35_client.get(NOTIFICATION_BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_update(self):
        self.kd35_client.post(COMMENT_BASE_URL, {
            'tweet_id': self.lbj23_tweet.id,
            'content': 'Good job, my bro! I am going to Worries BTW'
        })
        self.kd35_client.post(LIKE_BASE_URL, {
            'content_type': 'tweet',
            'object_id': self.lbj23_tweet.id,
        })
        notification = Notification.objects.filter(recipient=self.lbj23).first()
        url = NOTIFICATION_DETAIL_URL.format(notification.id)
        unread_count_url = NOTIFICATION_BASE_URL + 'unread-count/'

        # Not log-in  <Wayne Shih> 19-Mar-2022
        response = self.anonymous_client.put(url, {'unread': False})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # kd35 is not the notification owner  <Wayne Shih> 19-Mar-2022
        response = self.kd35_client.put(url, {'unread': False})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Method not allowed  <Wayne Shih> 19-Mar-2022
        response = self.lbj23_client.post(url, {'unread': False})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Missing param  <Wayne Shih> 19-Mar-2022
        response = self.lbj23_client.put(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')
        self.assertEqual(
            response.data['errors'],
            'Request is missing param(s): unread. All missing params are required to provide.'
        )

        # Invalid param  <Wayne Shih> 19-Mar-2022
        response = self.lbj23_client.put(url, {'unread': 12345})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')
        self.assertEqual(response.data['errors']['unread'][0], 'Must be a valid boolean.')

        # mark as read success  <Wayne Shih> 19-Mar-2022
        response = self.lbj23_client.get(unread_count_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread_count'], 2)
        response = self.lbj23_client.put(url, {'unread': False})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread'], False)
        response = self.lbj23_client.get(unread_count_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread_count'], 1)

        # mark as unread success  <Wayne Shih> 19-Mar-2022
        response = self.lbj23_client.put(url, {'unread': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread'], True)
        response = self.lbj23_client.get(unread_count_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread_count'], 2)

        # Will not modify fields other than 'unread'
        verb = notification.verb
        response = self.lbj23_client.put(url, {'verb': 'fake_verb', 'unread': False})
        notification.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(notification.verb, verb)
        self.assertNotEqual(notification.verb, 'fake_verb')

    def test_unread_count(self):
        url = NOTIFICATION_BASE_URL + 'unread-count/'

        # Not log-in  <Wayne Shih> 16-Mar-2022
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # login user lbj23 has 0 notification  <Wayne Shih> 16-Mar-2022
        response = self.lbj23_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread_count'], 0)

        # Method not allowed  <Wayne Shih> 16-Mar-2022
        response = self.kd35_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # login user lbj23 has 1 notification  <Wayne Shih> 16-Mar-2022
        self.kd35_client.post(COMMENT_BASE_URL, {
            'tweet_id': self.lbj23_tweet.id,
            'content': 'Good job, my bro! I am going to Worries BTW'
        })
        response = self.lbj23_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread_count'], 1)

        # login user kd35 has 0 notification  <Wayne Shih> 16-Mar-2022
        response = self.kd35_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread_count'], 0)

    def test_mark_all_as_read(self):
        unread_count_url = NOTIFICATION_BASE_URL + 'unread-count/'
        mark_read_url = NOTIFICATION_BASE_URL + 'mark-all-as-read/'

        # Not log-in  <Wayne Shih> 16-Mar-2022
        response = self.anonymous_client.post(mark_read_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # login user lbj23 has 0 notification  <Wayne Shih> 16-Mar-2022
        response = self.lbj23_client.post(mark_read_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['marked_count'], 0)

        # Method not allowed  <Wayne Shih> 16-Mar-2022
        response = self.kd35_client.get(mark_read_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # <Wayne Shih> 16-Mar-2022
        # lbj23 has 2 notifications and kd35 has 1 notification
        kd35_comment_id = self.kd35_client.post(COMMENT_BASE_URL, {
            'tweet_id': self.lbj23_tweet.id,
            'content': 'Good job, my bro! I am going to Worries BTW'
        }).data['id']
        self.kd35_client.post(LIKE_BASE_URL, {
            'content_type': 'tweet',
            'object_id': self.lbj23_tweet.id,
        })
        self.lbj23_client.post(LIKE_BASE_URL, {
            'content_type': 'comment',
            'object_id': kd35_comment_id,
        })

        response = self.lbj23_client.post(mark_read_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['marked_count'], 2)
        response = self.lbj23_client.get(unread_count_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread_count'], 0)
        response = self.kd35_client.get(unread_count_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread_count'], 1)
