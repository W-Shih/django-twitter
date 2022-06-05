# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#  Define Comment model that maps to DB comments_comment table
#
#  Ref:
#    - https://docs.djangoproject.com/en/3.2/topics/db/models/
#    - https://www.django-rest-framework.org/tutorial/1-serialization/#creating-a-model-to-work-with
#
# =================================================================================================
#    Date      Name                    Description of Change
# 05-Nov-2021  Wayne Shih              Initial create
# 27-Nov-2021  Wayne Shih              Update Comment ordering
# 24-Feb-2022  Wayne Shih              Add like_set as relationships “backward”
# 26-Feb-2022  Wayne Shih              Add comments for ContentType
# 26-May-2022  Wayne Shih              Add cached_user
# 27-May-2022  Wayne Shih              React to memcached helper
# 30-May-2022  Wayne Shih              React to utils file structure refactor
# 05-Jun-2022  Wayne Shih              React to tweet model denormalization for comments_count
# $HISTORY$
# =================================================================================================


from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save, pre_delete

from likes.models import Like
from tweets.models import Tweet
from utils.caches.memcached_helpers import MemcachedHelper
from comments.listeners import decrease_comments_count, increase_comments_count


class Comment(models.Model):
    # <Wayne Shih> 05-Nov-2021
    # This version supports "comments on tweet" only.
    # This version doesn't support "comments on comment".
    #
    # TODO:
    #   To support "comments on tweet and comment", need to use (content_type, content_object)
    #   together as a generic foreign key.
    #   We will use (content_type, content_object) together as a generic foreign key to
    #   implement "like" feature in the near future task.
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)
    content = models.CharField(max_length=140)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        index_together = (('tweet', 'created_at'),)
        ordering = ('created_at',)

    def __str__(self):
        message = '{created_at}, {user}-{user_id} says "{content}" on tweet-{tweet_id}'
        return message.format(
            created_at=self.created_at,
            user=self.user,
            user_id=self.user_id,
            content=self.content,
            tweet_id=self.tweet_id,
        )

    # <Wayne Shih> 24-Feb-2022
    # Write our own relationships “backward”
    #   - https://docs.djangoproject.com/en/4.0/topics/db/queries/#following-relationships-backward
    # content_type is recorded in django_content_type table.
    # get_for_model() here is to get model's metadata so that db knows the model.
    #   - https://docs.djangoproject.com/en/4.0/ref/contrib/contenttypes/#django.contrib.contenttypes.models.ContentTypeManager.get_for_model
    @property
    def like_set(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return Like.objects.filter(
            content_type=content_type,
            object_id=self.id,
        ).order_by('-created_at')

    @property
    def cached_user(self):
        return MemcachedHelper.get_object_through_cache(User, self.user_id)


# <Wayne Shih> 05-Jun-2022
# https://docs.djangoproject.com/en/3.1/ref/signals/#post-save
# https://docs.djangoproject.com/en/3.1/topics/signals/#listening-to-signals
post_save.connect(increase_comments_count, sender=Comment)
pre_delete.connect(decrease_comments_count, sender=Comment)
