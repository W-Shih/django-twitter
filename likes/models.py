# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#  Define like model that maps to DB likes_like table
#
#  Ref:
#    - https://docs.djangoproject.com/en/3.2/topics/db/models/
#    - https://www.django-rest-framework.org/tutorial/1-serialization/#creating-a-model-to-work-with
#
# =================================================================================================
#    Date      Name                    Description of Change
# 23-Feb-2021  Wayne Shih              Initial create
# 26-May-2022  Wayne Shih              Fetch user from cache
# 27-May-2022  Wayne Shih              React to memcached helper
# $HISTORY$
# =================================================================================================


from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from utils.memcached_helpers import MemcachedHelper


class Like(models.Model):
    # <Wayne Shih> 23-Feb-2022
    # User can like a tweet or a comment, so here we use a genetic type of id that references
    # either a tweet_id or a comment_id.
    # That is, user liked content_object at created_at
    # - https://docs.djangoproject.com/en/4.0/ref/contrib/contenttypes/#generic-relations
    # - https://www.django-rest-framework.org/api-guide/relations/#generic-relationships
    object_id = models.PositiveIntegerField()  # tweet_id or comment_id
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('user', 'content_type', 'object_id'),)
        index_together = (
            ('user', 'content_type', 'created_at'),
            ('content_type', 'object_id', 'created_at'),
        )

    def __str__(self):
        message = '{created_at}, {user}-{user_id} liked {content_type}-{object_id}'
        return message.format(
            created_at=self.created_at,
            user=self.user,
            user_id=self.user_id,
            content_type=self.content_type,
            object_id=self.object_id,
        )

    @property
    def cached_user(self):
        return MemcachedHelper.get_object_through_cache(User, self.user_id)
