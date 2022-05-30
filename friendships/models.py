# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#   Define Friendship model that maps to DB friendships_friendship table
#
#   Ref:
#    - https://docs.djangoproject.com/en/3.2/topics/db/models/
#    - https://www.django-rest-framework.org/tutorial/1-serialization/#creating-a-model-to-work-with
#
# =================================================================================================
#    Date      Name                    Description of Change
# 07-Sep-2021  Wayne Shih              Initial create
# 10-Oct-2021  Wayne Shih              React to pylint checks
# 05-Nov-2021  Wayne Shih              Fix pylint checks
# 30-Apr-2022  Wayne Shih              Add Django signal-listener
# 26-May-2022  Wayne Shih              Fetch user from cache
# 27-May-2022  Wayne Shih              React to memcached helper
# 30-May-2022  Wayne Shih              React to utils file structure refactor
# $HISTORY$
# =================================================================================================


from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save, pre_delete

from friendships.listeners import invalidate_followings_cache
from utils.caches.memcached_helpers import MemcachedHelper


class Friendship(models.Model):
    # <Wayne Shih> 07-Sep-2021
    # - https://docs.djangoproject.com/en/3.2/ref/models/fields/#django.db.models.ForeignKey
    # - https://docs.djangoproject.com/en/3.2/ref/models/fields/#django.db.models.ForeignKey.on_delete
    #
    # Following relationships “backward”
    # - https://docs.djangoproject.com/en/3.2/ref/models/fields/#django.db.models.ForeignKey.related_name
    # - https://docs.djangoproject.com/en/3.2/topics/db/queries/#backwards-related-objects
    # If a model Foo has a ForeignKey, instances of the foreign-key model will have access to a
    # Manager that returns all instances of the Foo model.
    # By default, this Manager is named FOO_set, where FOO is the source model name, lowercased.
    # This Manager returns QuerySets, which can be filtered and manipulated.
    # Example:
    # user = User.objects.filter(user=request.user)
    # user is a FK in Friendship, so it has a default Manger: friendship_set.
    # and user.friendship_set.all() returns all Friendship objects related to the user.
    # However, here needs to use related_name distinguish
    #   - Friendship objects related to the from_user
    #   - Friendship objects related to the to_user
    # so,
    # user.follower_friendship_set <-> Friendship objects that are the followers of user
    # user.following_friendship_set <-> Friendship objects that are the followings of user
    # In fact,
    # user.follower_friendship_set == Friendship.objects.filter(to_user=user)
    # user.following_friendship_set == Friendship.objects.filter(from_user=user)
    #
    from_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='following_friendship_set',
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='follower_friendship_set',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (
            ('from_user_id', 'created_at'),
            ('to_user_id', 'created_at'),
        )
        unique_together = (('from_user_id', 'to_user_id'),)
        ordering = ('-created_at',)

    def __str__(self):
        message = '-- Friendship-{id}: ' + \
                  '{from_user}-{from_user_id} following {to_user}-{to_user_id} ' + \
                  'at {created_at} --'
        return message.format(
            id=self.id,
            from_user=self.from_user,
            from_user_id=self.from_user_id,
            to_user=self.to_user,
            to_user_id=self.to_user_id,
            created_at=self.created_at,
        )

    @property
    def cached_from_user(self):
        return MemcachedHelper.get_object_through_cache(User, self.from_user_id)

    @property
    def cached_to_user(self):
        return MemcachedHelper.get_object_through_cache(User, self.to_user_id)


# <Wayne Shih> 29-Apr-2022
# https://docs.djangoproject.com/en/3.1/ref/signals/#post-save
# https://docs.djangoproject.com/en/3.1/topics/signals/#listening-to-signals
post_save.connect(invalidate_followings_cache, sender=Friendship)
pre_delete.connect(invalidate_followings_cache, sender=Friendship)
