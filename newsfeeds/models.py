# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#   Define Newsfeed model that maps to DB newsfeeds_newsfeed table
#
#   Ref:
#   - https://docs.djangoproject.com/en/3.2/topics/db/models/
#   - https://www.django-rest-framework.org/tutorial/1-serialization/#creating-a-model-to-work-with
#
# =================================================================================================
#    Date      Name                    Description of Change
# 17-Oct-2021  Wayne Shih              Initial create
# 27-May-2022  Wayne Shih              Add cached_tweet
# 29-May-2022  Wayne Shih              Add Django signal-listener for user newsfeeds cache
# $HISTORY$
# =================================================================================================


from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save

from newsfeeds.listeners import push_newsfeed_to_cache
from tweets.models import Tweet
from utils.memcached_helpers import MemcachedHelper


class NewsFeed(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (('user', 'created_at'),)
        unique_together = (('user', 'tweet'),)
        ordering = ('user', '-created_at')

    def __str__(self):
        return f'-- {self.created_at} inbox of {self.user}: {self.tweet} --'

    @property
    def cached_tweet(self):
        return MemcachedHelper.get_object_through_cache(Tweet, self.tweet_id)


# <Wayne Shih> 29-Apr-2022
# https://docs.djangoproject.com/en/3.1/ref/signals/#post-save
# https://docs.djangoproject.com/en/3.1/topics/signals/#listening-to-signals
post_save.connect(push_newsfeed_to_cache, sender=NewsFeed)
