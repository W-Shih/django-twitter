# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#   Account services provide User helpers for other APIs
#
# =================================================================================================
#    Date      Name                    Description of Change
# 25-May-2022  Wayne Shih              Initial create
# 27-May-2022  Wayne Shih              React to memcached helper
# 29-May-2022  Wayne Shih              Fix style
# $HISTORY$
# =================================================================================================


from django.conf import settings
from django.core.cache import caches

from accounts.models import UserProfile
from twitter.caches import USER_PROFILE_PATTERN


cache = caches['default'] if not settings.TESTING else caches['testing']


class UserService(object):

    # <Wayne Shih> 27-May-2022
    # Keep this for profile cache specifically instead of using memcached helper
    # because profile key pattern is different than others as well as it needs
    # get_or_create() instead of simple get()
    @classmethod
    def get_profile_through_cache(cls, user_id):
        key = USER_PROFILE_PATTERN.format(user_id=user_id)
        profile = cache.get(key)
        if profile is not None:
            return profile

        profile, _ = UserProfile.objects.get_or_create(user_id=user_id)
        cache.set(key, profile)
        return profile

    @classmethod
    def invalidate_profile_cache(cls, user_id):
        key = USER_PROFILE_PATTERN.format(user_id=user_id)
        cache.delete(key)
