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
# $HISTORY$
# =================================================================================================


from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models

from likes.models import Like
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
