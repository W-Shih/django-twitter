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
# 04-Nov-2021  Wayne Shih              React to adding anonymous_client to base class
# 06-Nov-2021  Wayne Shih              Modify some assertEqual to check set instead of list
# 13-Nov-2021  Wayne Shih              Update non_existing_user_id larger to Fix test fail
# 23-Mar-2022  Wayne Shih              React to user-related serializer changes
# 02-Apr-2022  Wayne Shih              Add tests for friendships pagination
# 03-Apr-2022  Wayne Shih              Add tests for followers & followings pagination, react to adding has_followed
# $HISTORY$
# =================================================================================================


from math import ceil

from rest_framework import status
from rest_framework.test import APIClient

from friendships.api.pagination import FriendshipPagination
from friendships.models import Friendship
from testing.testcases import TestCase


DRF_API_URL = '/api/friendships/'
FOLLOWERS_URL = '/api/friendships/{}/followers/'
FOLLOWINGS_URL = '/api/friendships/{}/followings/'
FOLLOW_URL = '/api/friendships/{}/follow/'
UNFOLLOW_URL = '/api/friendships/{}/unfollow/'


class FriendshipApiTests(TestCase):

    def setUp(self):
        self.lbj23 = self.create_user(username='lbj23')
        self.lbj23_client = APIClient()
        self.lbj23_client.force_authenticate(self.lbj23)

        self.mj23 = self.create_user(username='mj23')
        self.mj23_client = APIClient()
        self.mj23_client.force_authenticate(self.mj23)

        self.kb24, self.kb24_client = self.create_user_and_auth_client(username='kb24')
        self.kd35, self.kd35_client = self.create_user_and_auth_client(username='kd35')

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
        self.assertEqual(set(followers[0].keys()), {'from_user', 'created_at', 'has_followed'})
        self.assertEqual(
            set(followers[0].get('from_user')),
            {'id', 'username', 'nickname', 'avatar_url'}
        )
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
        # <Wayne Shih> 13-Nov-2021
        # As number of tests increase, so does user_id in DB.
        # Therefor, update non_existing_user_id larger to Fix test fail.
        non_existing_user_id = 10000
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
        self.assertEqual(set(followings[0].keys()), {'user', 'created_at', 'has_followed'})
        self.assertEqual(
            set(followings[0].get('user')),
            {'id', 'username', 'nickname', 'avatar_url'}
        )
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
        self.assertEqual(set(response.data.keys()), {'success', 'following'})
        self.assertEqual(
            set(response.data['following'].keys()),
            {'user', 'created_at', 'has_followed'}
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

    def test_friendships_pagination(self):
        page_size = FriendshipPagination.page_size
        max_page_size = FriendshipPagination.max_page_size

        # test FOLLOWINGS_URL - no pagination params  <Wayne Shih> 02-Apr-2022
        url = FOLLOWINGS_URL.format(self.kd35.id)
        num_followings = page_size * 3
        for i in range(num_followings):
            following = self.create_user(username=f'kd35_following{i}')
            Friendship.objects.create(from_user=self.kd35, to_user=following)

        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(isinstance(response.data['results'], list), True)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['count'], num_followings)
        self.assertEqual(response.data['has_previous'], False)
        self.assertEqual(response.data['has_next'], True)
        self.assertEqual(response.data['previous'], None)
        self.assertEqual('?page=2' in response.data['next'], True)
        self.assertEqual(response.data['num_pages'], ceil(num_followings / page_size))
        self.assertEqual(response.data['page_number'], 1)

        # <Wayne Shih> 02-Apr-2022
        # test FOLLOWINGS_URL - customized page_size won't exceed max_page_size
        response = self.anonymous_client.get(url, {'page_size': max_page_size + 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(isinstance(response.data['results'], list), True)
        self.assertEqual(len(response.data['results']), min(max_page_size, num_followings))
        self.assertEqual(response.data['count'], num_followings)
        self.assertEqual(response.data['has_previous'], False)
        self.assertEqual(response.data['has_next'], num_followings > max_page_size)
        self.assertEqual(response.data['previous'], None)
        if num_followings > max_page_size:
            self.assertEqual('?page=2' in response.data['next'], True)
        else:
            self.assertEqual(response.data['next'], None)
        self.assertEqual(response.data['num_pages'], ceil(num_followings / (max_page_size + 1)))
        self.assertEqual(response.data['page_number'], 1)

        # test FOLLOWINGS_URL - non-existing page number  <Wayne Shih> 02-Apr-2022
        non_existing_page_num = 0
        response = self.anonymous_client.get(url, {'page': non_existing_page_num})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'Invalid page.')

        non_existing_page_num = ceil(num_followings / page_size) + 1
        response = self.anonymous_client.get(url, {'page': non_existing_page_num})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'Invalid page.')

        # test FOLLOWERS_URL - no pagination params  <Wayne Shih> 02-Apr-2022
        url = FOLLOWERS_URL.format(self.kb24.id)
        num_followers = page_size - 1
        for i in range(num_followers):
            follower = self.create_user(username=f'kb24_follower{i}')
            Friendship.objects.create(from_user=follower, to_user=self.kb24)

        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), num_followers)
        self.assertEqual(response.data['count'], num_followers)
        self.assertEqual(response.data['has_previous'], False)
        self.assertEqual(response.data['has_next'], False)
        self.assertEqual(response.data['previous'], None)
        self.assertEqual(response.data['next'], None)
        self.assertEqual(response.data['num_pages'], ceil(num_followers / page_size))
        self.assertEqual(response.data['page_number'], 1)

        # test FOLLOWERS_URL - pagination params  <Wayne Shih> 02-Apr-2022
        customized_page_size = page_size // 2
        response = self.anonymous_client.get(url, {'page_size': customized_page_size})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), customized_page_size)
        self.assertEqual(response.data['count'], num_followers)
        self.assertEqual(response.data['previous'], None)
        self.assertEqual(f'?page=2&page_size={customized_page_size}' in response.data['next'], True)
        self.assertEqual(response.data['has_previous'], False)
        self.assertEqual(response.data['has_next'], True)
        self.assertEqual(response.data['num_pages'], ceil(num_followers / customized_page_size))
        self.assertEqual(response.data['page_number'], 1)

        response = self.anonymous_client.get(url, {'page': 2, 'page_size': customized_page_size})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], num_followers)
        self.assertEqual(len(response.data['results']), num_followers - customized_page_size)
        self.assertEqual(response.data['has_previous'], True)
        self.assertEqual(response.data['has_next'], False)
        self.assertEqual(f'?page_size={customized_page_size}' in response.data['previous'], True)
        self.assertEqual(response.data['next'], None)
        self.assertEqual(response.data['num_pages'], ceil(num_followers / customized_page_size))
        self.assertEqual(response.data['page_number'], 2)

    def test_followers_pagination(self):
        page_size = FriendshipPagination.page_size
        url = FOLLOWERS_URL.format(self.kb24.id)
        num_followers = page_size * 2
        for i in range(num_followers):
            user = self.create_user(username=f'kb24_follower{i}')
            Friendship.objects.create(from_user=user, to_user=self.kb24)
            if user.id % 2 == 0:
                Friendship.objects.create(from_user=self.kd35, to_user=user)

        # kd has followed user with even id  <Wayne Shih> 03-Apr-2022
        response = self.kd35_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['count'], num_followers)
        for result in response.data['results']:
            user_id = result['from_user']['id']
            has_kd_followed = (user_id % 2 == 0)
            self.assertEqual(result['has_followed'], has_kd_followed)
        self.assertEqual(response.data['previous'], None)
        self.assertEqual('?page=2' in response.data['next'], True)
        self.assertEqual(response.data['has_previous'], False)
        self.assertEqual(response.data['has_next'], True)
        self.assertEqual(response.data['num_pages'], ceil(num_followers / page_size))
        self.assertEqual(response.data['page_number'], 1)

        # anonymous hasn't followed any user  <Wayne Shih> 03-Apr-2022
        response = self.anonymous_client.get(url, {'page': 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], num_followers)
        self.assertEqual(len(response.data['results']), page_size)
        for result in response.data['results']:
            self.assertEqual(result['has_followed'], False)
        self.assertEqual(response.data['num_pages'], ceil(num_followers / page_size))
        self.assertEqual(response.data['page_number'], 2)
        self.assertEqual(response.data['previous'].endswith('/followers/'), True)
        self.assertEqual(response.data['next'], None)
        self.assertEqual(response.data['has_previous'], True)
        self.assertEqual(response.data['has_next'], False)

    def test_followings_pagination(self):
        page_size = FriendshipPagination.page_size
        url = FOLLOWINGS_URL.format(self.kd35.id)
        num_followings = page_size * 2
        for i in range(num_followings):
            user = self.create_user(username=f'kd35_following{i}')
            Friendship.objects.create(from_user=self.kd35, to_user=user)
            if user.id % 2 == 0:
                Friendship.objects.create(from_user=self.kb24, to_user=user)

        # kd has followed all his followings  <Wayne Shih> 03-Apr-2022
        response = self.kd35_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['count'], num_followings)
        for result in response.data['results']:
            self.assertEqual(result['has_followed'], True)
        self.assertEqual(response.data['num_pages'], ceil(num_followings / page_size))
        self.assertEqual(response.data['page_number'], 1)
        self.assertEqual(response.data['previous'], None)
        self.assertEqual('?page=2' in response.data['next'], True)
        self.assertEqual(response.data['has_previous'], False)
        self.assertEqual(response.data['has_next'], True)

        # kb has followed user with even id  <Wayne Shih> 03-Apr-2022
        response = self.kb24_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], num_followings)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['num_pages'], ceil(num_followings / page_size))
        self.assertEqual(response.data['page_number'], 1)
        self.assertEqual(response.data['has_previous'], False)
        self.assertEqual(response.data['has_next'], True)
        self.assertEqual(response.data['previous'], None)
        self.assertEqual('?page=2' in response.data['next'], True)
        for result in response.data['results']:
            user_id = result['user']['id']
            has_kb_followed = (user_id % 2 == 0)
            self.assertEqual(result['has_followed'], has_kb_followed)

        # anonymous hasn't followed any user  <Wayne Shih> 03-Apr-2022
        response = self.anonymous_client.get(url, {'page': 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for result in response.data['results']:
            self.assertEqual(result['has_followed'], False)
        self.assertEqual(response.data['has_previous'], True)
        self.assertEqual(response.data['has_next'], False)
        self.assertEqual(response.data['previous'].endswith('/followings/'), True)
        self.assertEqual(response.data['next'], None)
        self.assertEqual(response.data['count'], num_followings)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['num_pages'], ceil(num_followings / page_size))
        self.assertEqual(response.data['page_number'], 2)
