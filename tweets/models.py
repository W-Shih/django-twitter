# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#       Define Tweet model that maps to DB tweets_tweet table
#
#       Ref:
#         - https://docs.djangoproject.com/en/3.2/topics/db/models/
#         - https://www.django-rest-framework.org/tutorial/1-serialization/#creating-a-model-to-work-with
#
# =================================================================================================
#    Date      Name                    Description of Change
# 30-Aug-2021  Wayne Shih              Initial create
# 07-Sep-2021  Wayne Shih              Update __str__ format
# 10-Oct-2021  Wayne Shih              React to pylint checks
# $HISTORY$
# =================================================================================================


from django.contrib.auth.models import User
from django.db import models

from utils.time_helpers import utc_now


class Tweet(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (('user', 'created_at'),)
        ordering = ('user_id', '-created_at')

    def __str__(self):
        return '-- Tweet-{id}: {user}-{user_id} -- {created_at} -- {content} --'.format(
            id=self.id,
            user=self.user,
            user_id=self.user_id,
            created_at=self.created_at,
            content=self.content,
        )

    @property
    def hours_to_now(self):
        return (utc_now() - self.created_at).seconds // 3600
