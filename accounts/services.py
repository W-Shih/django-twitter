# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#   Account services provide User helpers for other APIs
#
# =================================================================================================
#    Date      Name                    Description of Change
# 25-May-2022  Wayne Shih              Initial create
# $HISTORY$
# =================================================================================================


from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import caches

from accounts.models import UserProfile
from twitter.caches import USER_PATTERN, USER_PROFILE_PATTERN


cache = caches['default'] if not settings.TESTING else caches['testing']


class UserService(object):

    @classmethod
    def get_user_through_cache(cls, user_id):
        key = USER_PATTERN.format(user_id=user_id)
        user = cache.get(key)
        if user is not None:
            return user

        # <Wayne Shih> 25-May-2022
        # Here expects the user exists in DB, if not, let it throw an error
        # - https://docs.djangoproject.com/en/4.0/ref/models/querysets/#get
        user = User.objects.get(id=user_id)
        cache.set(key, user)
        return user

    @classmethod
    def invalidate_user_cache(cls, user_id):
        key = USER_PATTERN.format(user_id=user_id)
        cache.delete(key)

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
