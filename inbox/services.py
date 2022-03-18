# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#   Notification services provide notification helpers for other APIs
#
# =================================================================================================
#    Date      Name                    Description of Change
# 12-Mar-2022  Wayne Shih              Initial create
# 17-Mar-2022  Wayne Shih              Update verb strings for front-end to render hyperlinks
# $HISTORY$
# =================================================================================================


from django.contrib.contenttypes.models import ContentType
from notifications.signals import notify

from comments.models import Comment
from tweets.models import Tweet


class NotificationService(object):

    @classmethod
    def send_comment_notification(cls, comment):
        if comment.user_id == comment.tweet.user_id:
            return
        notify.send(
            sender=comment.user,
            verb='commented on your tweet {target_link_to_render}',
            target=comment.tweet,
            recipient=comment.tweet.user,
        )

    @classmethod
    def send_like_notification(cls, like):
        target = like.content_object
        if like.user_id == target.user_id:
            return

        content_type = 'unknown'
        if like.content_type == ContentType.objects.get_for_model(Tweet):
            content_type = 'tweet'
        elif like.content_type == ContentType.objects.get_for_model(Comment):
            content_type = 'comment'

        notify.send(
            sender=like.user,
            verb=f'liked on your {content_type} {"{target_link_to_render}"}',
            target=target,
            recipient=target.user,
        )
