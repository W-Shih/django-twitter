# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#           friendships api unit tests
#
# =================================================================================================
#    Date      Name                    Description of Change
# 09-Sep-2021  Wayne Shih              Initial create
# 10-Oct-2021  Wayne Shih              React to pylint checks
# $HISTORY$
# =================================================================================================


from rest_framework import status
from rest_framework.test import APIClient

from friendships.models import Friendship
from testing.testcases import TestCase


DRF_API_URL = '/api/friendships/'
FOLLOWERS_URL = '/api/friendships/{}/followers/'
FOLLOWINGS_URL = '/api/friendships/{}/followings/'
FOLLOW_URL = '/api/friendships/{}/follow/'
UNFOLLOW_URL = '/api/friendships/{}/unfollow/'


class FriendshipApiTests(TestCase):

    def setUp(self):
        self.anonymous_client = APIClient()

        self.lbj23 = self.create_user(username='lbj23')
        self.lbj23_client = APIClient()
        self.lbj23_client.force_authenticate(self.lbj23)

        self.mj23 = self.create_user(username='mj23')
        self.mj23_client = APIClient()
        self.mj23_client.force_authenticate(self.mj23)

        for i in range(2):
            follower = self.create_user(username=f'lbj23_follower{i}')
            Friendship.objects.create(from_user=follower, to_user=self.lbj23)

        for i in range(3):
            following = self.create_user(username=f'lbj23_following{i}')
            Friendship.objects.create(from_user=self.lbj23, to_user=following)

    def test_drf_api_page(self):
        response = self.anonymous_client.get(DRF_API_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_followers(self):
        non_existing_user_id = 100
        url = FOLLOWERS_URL.format(non_existing_user_id)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        url = FOLLOWERS_URL.format(self.lbj23.id)
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.anonymous_client.get(url)
        followers = response.data['followers']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(isinstance(followers, list), True)
        self.assertEqual(len(followers), 2)
        self.assertEqual(list(followers[0].keys()), ['from_user', 'created_at'])
        self.assertEqual(list(followers[0].get('from_user')), ['id', 'username'])
        # <Wayne Shih> 06-Sep-2021
        # test order by '-created_at'
        for i in range(len(followers) - 1):
            self.assertEqual(
                followers[i]['created_at'] > followers[i + 1]['created_at'],
                True
            )
        self.assertEqual(followers[0]['from_user']['username'], 'lbj23_follower1')
        self.assertEqual(followers[1]['from_user']['username'], 'lbj23_follower0')

    def test_followings(self):
        non_existing_user_id = 50
        url = FOLLOWINGS_URL.format(non_existing_user_id)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        url = FOLLOWINGS_URL.format(self.lbj23.id)
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.anonymous_client.get(url)
        followings = response.data['followings']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(isinstance(followings, list), True)
        self.assertEqual(len(followings), 3)
        self.assertEqual(list(followings[0].keys()), ['user', 'created_at'])
        self.assertEqual(list(followings[0].get('user')), ['id', 'username'])
        # <Wayne Shih> 06-Sep-2021
        # test order by '-created_at'
        for i in range(len(followings) - 1):
            self.assertEqual(
                followings[i]['created_at'] > followings[i + 1]['created_at'],
                True
            )
        for i in range(len(followings)):
            self.assertEqual(
                followings[i]['user']['username'],
                f'lbj23_following{len(followings) - 1 - i}'
            )

    def test_follow(self):
        url = FOLLOW_URL.format(self.mj23.id)

        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.mj23_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.mj23_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['errors']['message'][0],
            'You can not follow yourself.'
        )

        count = Friendship.objects.count()
        response = self.lbj23_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Friendship.objects.count(), count + 1)
        self.assertEqual(list(response.data.keys()), ['success', 'following'])
        self.assertEqual(
            list(response.data['following'].keys()),
            ['user', 'created_at']
        )
        self.assertEqual(response.data['following']['user']['id'], self.mj23.id)

        count = Friendship.objects.count()
        response = self.lbj23_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['duplicate'], True)
        self.assertEqual(Friendship.objects.count(), count)

        count = Friendship.objects.count()
        response = self.mj23_client.post(FOLLOW_URL.format(self.lbj23.id))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Friendship.objects.count(), count + 1)

        non_existing_user_id = 100
        url = FOLLOW_URL.format(non_existing_user_id)
        response = self.mj23_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unfollow(self):
        url = UNFOLLOW_URL.format(self.mj23.id)

        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.mj23_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.mj23_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'You cannot unfollow yourself.')

        Friendship.objects.create(from_user=self.lbj23, to_user=self.mj23)
        count = Friendship.objects.count()
        response = self.lbj23_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['num_deleted'], 1)
        self.assertEqual(Friendship.objects.count(), count - 1)

        count = Friendship.objects.count()
        response = self.lbj23_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['num_deleted'], 0)
        self.assertEqual(Friendship.objects.count(), count)
