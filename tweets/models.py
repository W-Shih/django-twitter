# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#   Define Tweet model that maps to DB tweets_tweet table
#
#   Ref:
#    - https://docs.djangoproject.com/en/3.2/topics/db/models/
#    - https://www.django-rest-framework.org/tutorial/1-serialization/#creating-a-model-to-work-with
#
# =================================================================================================
#    Date      Name                    Description of Change
# 30-Aug-2021  Wayne Shih              Initial create
# 07-Sep-2021  Wayne Shih              Update __str__ format
# 10-Oct-2021  Wayne Shih              React to pylint checks
# 05-Nov-2021  Wayne Shih              Fix pylint checks
# 24-Feb-2022  Wayne Shih              Add like_set as relationships “backward”
# 26-Feb-2022  Wayne Shih              Add comments for ContentType
# 25-Mar-2022  Wayne Shih              Add TweetPhoto model
# 30-Mar-2022  Wayne Shih              Update TweetPhoto model's index
# 26-May-2022  Wayne Shih              Fetch user from cache
# 27-May-2022  Wayne Shih              React to memcached helper, add Django signal-listener
# $HISTORY$
# =================================================================================================


from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save, pre_delete

from likes.models import Like
from tweets.constants import TWEET_PHOTO_STATUS_CHOICES, TweetPhotoStatus
from utils.memcached_helpers import MemcachedHelper
from utils.listeners import invalidate_object_cache
from utils.time_helpers import utc_now


class Tweet(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (('user', 'created_at'),)
        ordering = ('user_id', '-created_at')

    def __str__(self):
        message = '-- Tweet-{id}: {user}-{user_id} -- {created_at} -- {content} --'
        return message.format(
            id=self.id,
            user=self.user,
            user_id=self.user_id,
            created_at=self.created_at,
            content=self.content,
        )

    @property
    def hours_to_now(self):
        return (utc_now() - self.created_at).seconds // 3600

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


class TweetPhoto(models.Model):
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    file = models.FileField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # <Wayne Shih> 25-Mar-2022
    # https://docs.djangoproject.com/en/4.0/ref/models/fields/#django.db.models.Field.choices
    status = models.IntegerField(
        default=TweetPhotoStatus.PENDING,
        choices=TWEET_PHOTO_STATUS_CHOICES,
    )
    order = models.IntegerField(default=0)
    has_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        index_together = (
            ('tweet_id', 'status', 'order'),
            ('user_id', 'created_at'),
            ('has_deleted', 'deleted_at'),
            ('status', 'created_at'),
        )
        ordering = ('tweet_id', 'status', 'order')

    def __str__(self):
        message = 'TweetPhoto-[{id}] in tweet-[{tweet_id}] by [{user}]-[{user_id}] ' \
                  'with order-[{order}] created at [{created_at}].\n' \
                  'File: [{file}]'
        return message.format(
            id=self.id,
            tweet_id=self.tweet_id,
            user=self.user,
            user_id=self.user_id,
            order=self.order,
            created_at=self.created_at,
            file=self.file,
        )

# <Wayne Shih> 29-Apr-2022
# https://docs.djangoproject.com/en/3.1/ref/signals/#post-save
# https://docs.djangoproject.com/en/3.1/topics/signals/#listening-to-signals
post_save.connect(invalidate_object_cache, sender=Tweet)
pre_delete.connect(invalidate_object_cache, sender=Tweet)
