# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#   Friendship services provide Friendship helpers for other APIs
#
# =================================================================================================
#    Date      Name                    Description of Change
# 18-Oct-2021  Wayne Shih              Initial create
# 03-Apr-2022  Wayne Shih              Add get_has_followed()
# 30-Apr-2022  Wayne Shih              Add get_following_user_id_set() & invalidate_followings_cache()
# 26-May-2022  Wayne Shih              Add print to debug github travis CI
# 26-May-2022  Wayne Shih              Remove debug print for github travis CI
# 12-Jun-2022  Wayne Shih              Deprecate get_followers()
# $HISTORY$
# =================================================================================================


from django.conf import settings
from django.core.cache import caches

from friendships.models import Friendship
from twitter.caches import FOLLOWINGS_PATTERN

cache = caches['default'] if not settings.TESTING else caches['testing']


class FriendshipService(object):

    @classmethod
    def get_follower_ids(cls, user_id):
        follower_friendships = Friendship.objects.filter(to_user_id=user_id)
        follower_ids = [
            friendship.from_user_id
            for friendship in follower_friendships
        ]
        return follower_ids

    @classmethod
    def get_following_user_id_set(cls, from_user_id):
        key = FOLLOWINGS_PATTERN.format(user_id=from_user_id)
        following_user_id_set = cache.get(key)
        if following_user_id_set is not None:
            return following_user_id_set

        friendships = Friendship.objects.filter(from_user_id=from_user_id)
        following_user_id_set = {
            friendship.to_user_id for friendship in friendships
        }
        cache.set(key, following_user_id_set)
        return following_user_id_set

    @classmethod
    def invalidate_followings_cache(cls, from_user_id):
        key = FOLLOWINGS_PATTERN.format(user_id=from_user_id)
        cache.delete(key)
