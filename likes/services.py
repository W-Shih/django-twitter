# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#   Like services provide Like helpers for other APIs
#
# =================================================================================================
#    Date      Name                    Description of Change
# 11-Mar-2022  Wayne Shih              Initial create
# $HISTORY$
# =================================================================================================


from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from likes.models import Like


class LikeService(object):

    @classmethod
    def get_has_liked(cls, user: User, target):
        if user.is_anonymous:
            return False
        return Like.objects.filter(
            user_id=user.id,
            content_type=ContentType.objects.get_for_model(target.__class__),
            object_id=target.id,
        ).exists()
