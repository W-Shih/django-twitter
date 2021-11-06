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
# $HISTORY$
# =================================================================================================


from django.contrib.auth.models import User
from django.db import models

from tweets.models import Tweet


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
        ordering = ('-created_at',)

    def __str__(self):
        message = '{created_at}, {user}-{user_id} says "{content}" on tweet-{tweet_id}'
        return message.format(
            created_at=self.created_at,
            user=self.user,
            user_id=self.user_id,
            content=self.content,
            tweet_id=self.tweet_id,
        )
