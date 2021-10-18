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
# $HISTORY$
# =================================================================================================


from django.contrib.auth.models import User
from django.db import models

from tweets.models import Tweet


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
