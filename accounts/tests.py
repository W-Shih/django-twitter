# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#           userprofile model unit tests
#
# =================================================================================================
#    Date      Name                    Description of Change
# 19-Mar-2021  Wayne Shih              Initial create
# $HISTORY$
# =================================================================================================


from accounts.models import UserProfile
from testing.testcases import TestCase


class UserProfileTests(TestCase):

    def test_user_profile_model_attributes(self):
        self.assertEqual(hasattr(UserProfile, 'id'), True)
        self.assertEqual(hasattr(UserProfile, 'user'), True)
        self.assertEqual(hasattr(UserProfile, 'user_id'), True)
        self.assertEqual(hasattr(UserProfile, 'nickname'), True)
        self.assertEqual(hasattr(UserProfile, 'avatar'), True)
        self.assertEqual(hasattr(UserProfile, 'created_at'), True)
        self.assertEqual(hasattr(UserProfile, 'updated_at'), True)

    def test_added_profile_property(self):
        lbj23 = self.create_user(username='cavs_lbj23')
        self.assertEqual(UserProfile.objects.count(), 0)

        lbj23_profile = lbj23.profile
        self.assertEqual(isinstance(lbj23_profile, UserProfile), True)
        self.assertEqual(UserProfile.objects.count(), 1)

        self.assertEqual(isinstance(lbj23.profile, UserProfile), True)
        self.assertEqual(UserProfile.objects.count(), 1)

    def test_user_profile_str(self):
        lbj23 = self.create_user(username='cavs_lbj23')
        lbj23_profile = lbj23.profile
        self.assertEqual(
            str(lbj23_profile.created_at) in str(lbj23_profile),
            True
        )
        self.assertEqual(
            str(lbj23_profile.user_id) in str(lbj23_profile),
            True
        )
        message = 'Profile {user}-{user_id} with nickname-{nickname} and avatar-{avatar}' \
                  'was created at {created_at} and updated at {updated_at}.'
        self.assertEqual(message.format(
            user=lbj23_profile.user,
            user_id=lbj23_profile.user_id,
            nickname=lbj23_profile.nickname,
            avatar=lbj23_profile.avatar,
            created_at=lbj23_profile.created_at,
            updated_at=lbj23_profile.updated_at,
        ), str(lbj23_profile))
