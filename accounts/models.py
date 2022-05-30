# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#  Define UserProfile model that maps to DB accounts_userprofile table
#
#  Ref:
#    - https://docs.djangoproject.com/en/3.2/topics/db/models/
#    - https://www.django-rest-framework.org/tutorial/1-serialization/#creating-a-model-to-work-with
#
# =================================================================================================
#    Date      Name                    Description of Change
# 19-Mar-2022  Wayne Shih              Initial create
# 23-Mar-2022  Wayne Shih              Update UserProfile's __str__
# 26-May-2022  Wayne Shih              Add Django signal-listener
# 27-May-2022  Wayne Shih              React to memcached helper
# 30-May-2022  Wayne Shih              React to utils file structure refactor
# $HISTORY$
# =================================================================================================


from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save, pre_delete

from accounts.listeners import invalidate_profile_cache
from utils.caches.listeners import invalidate_object_cache


class UserProfile(models.Model):
    # <Wayne Shih> 19-Mar-2022
    # OneToOneField is a ForeignKey with the "unique" constraint
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    nickname = models.CharField(null=True, max_length=100)
    avatar = models.FileField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        message = 'Profile-[{id}]: {user}-[{user_id}] with nickname-[{nickname}] and ' \
                  'avatar-[{avatar}] was created at {created_at} and updated at {updated_at}.'
        return message.format(
            id=self.id,
            user=self.user,
            user_id=self.user_id,
            nickname=self.nickname,
            avatar=self.avatar,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


def get_profile(user: User):
    from accounts.services import UserService

    if hasattr(user, '_cached_user_profile'):
        return getattr(user, '_cached_user_profile')

    # <Wayne Shih> 19-Mar-2022
    # Consider UserProfile is a new added model, so previous users might not have their
    # user profiles created. In this case, here performs lazy creation of user profile
    # for these users.
    profile = UserService.get_profile_through_cache(user.id)
    setattr(user, '_cached_user_profile', profile)
    return profile


# <Wayne Shih> 19-Mar-2022
# Python will execute this line when it starts so that we are able to add our own attributes
# or methods to an object from their party package.
User.profile = property(get_profile)


# <Wayne Shih> 29-Apr-2022
# https://docs.djangoproject.com/en/3.1/ref/signals/#post-save
# https://docs.djangoproject.com/en/3.1/topics/signals/#listening-to-signals
post_save.connect(invalidate_object_cache, sender=User)
pre_delete.connect(invalidate_object_cache, sender=User)

post_save.connect(invalidate_profile_cache, sender=UserProfile)
pre_delete.connect(invalidate_profile_cache, sender=UserProfile)
