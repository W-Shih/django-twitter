# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#           Friendship model unit tests
#
# =================================================================================================
#    Date      Name                    Description of Change
# 07-Sep-2021  Wayne Shih              Initial create
# 10-Oct-2021  Wayne Shih              React to pylint checks
# 17-Oct-2021  Wayne Shih              Fix pylint checks
# $HISTORY$
# =================================================================================================


import re

from testing.testcases import TestCase
from friendships.models import Friendship


class FriendshipTest(TestCase):

    def setUp(self):
        self.user_1 = self.create_user(username='cavs_lbj23')
        self.user_2 = self.create_user(username='lakers_lbj23')
        self.user_3 = self.create_user(username='bulls_mj23')

        self.friendship_1_3 = Friendship.objects.create(
            from_user=self.user_1,
            to_user=self.user_3
        )
        self.friendship_2_3 = Friendship.objects.create(
            from_user=self.user_2,
            to_user=self.user_3
        )

    def test_friendship_model_attributes(self):
        self.assertEqual(hasattr(Friendship, 'id'), True)
        self.assertEqual(hasattr(Friendship, 'from_user'), True)
        self.assertEqual(hasattr(Friendship, 'from_user_id'), True)
        self.assertEqual(hasattr(Friendship, 'to_user'), True)
        self.assertEqual(hasattr(Friendship, 'to_user_id'), True)
        self.assertEqual(hasattr(Friendship, 'created_at'), True)

    def test_friendship_model(self):
        friendships = Friendship.objects.all()
        self.assertEqual(friendships.count(), 2)
        # <Wayne Shih> 07-Sep-2021
        # test order by '-created_at'
        self.assertEqual(friendships.first().from_user, self.user_2)
        self.assertEqual(friendships.first().to_user, self.user_3)

        self.user_2.delete()
        self.assertEqual(friendships.first().from_user, None)

        self.assertEqual(hasattr(self.user_1, 'following_friendship_set'), True)
        self.assertEqual(hasattr(self.user_1, 'follower_friendship_set'), True)

    def test_friendship_meta(self):
        self.assertEqual(len(Friendship._meta.index_together), 2)
        self.assertEqual(len(Friendship._meta.unique_together), 1)

        for _ in Friendship._meta.index_together:
            self.assertEqual(
                bool(re.search('from_user(.*?)created_at', str(Friendship._meta.index_together)))
                or
                bool(re.search('to_user(.*?)created_at', str(Friendship._meta.index_together))),
                True
            )

        self.assertEqual(
            bool(re.search('from_user(.*?)to_user', str(Friendship._meta.unique_together))),
            True
        )

    def test_auto_now_add(self):
        user_1 = self.create_user(username='mavs_d77')
        user_2 = self.create_user(username='lakers_kb24')
        friendship = Friendship.objects.create(from_user=user_1, to_user=user_2)

        old_created_time = friendship.created_at
        friendship.from_user = user_2
        friendship.to_user = user_1
        friendship.save()
        self.assertEqual(old_created_time, friendship.created_at)

    def test_friendship_str(self):
        # print(self.friendship_1_3)
        self.assertEqual(
            str(self.friendship_1_3.created_at) in str(self.friendship_1_3),
            True
        )
        self.assertEqual(
            str(self.friendship_1_3.from_user.id) in str(self.friendship_1_3),
            True
        )
        self.assertEqual(
            str(self.friendship_1_3.to_user.id) in str(self.friendship_1_3),
            True
        )

        message = f'-- Friendship-{self.friendship_1_3.id}: ' + \
                  f'{self.friendship_1_3.from_user}-{self.friendship_1_3.from_user_id} ' + \
                  'following ' + \
                  f'{self.friendship_1_3.to_user}-{self.friendship_1_3.to_user_id} ' + \
                  f'at {self.friendship_1_3.created_at} --'
        self.assertEqual(message, str(self.friendship_1_3))
