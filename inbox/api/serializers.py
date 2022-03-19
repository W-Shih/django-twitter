# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#       - Serializer for notifications api
#
#       - Serializers allow complex data such as querysets and model instances to be converted to
#         native Python datatypes that can then be easily rendered into JSON, XML or other content
#         types.
#       - Can be used as a validator to validate if request is valid
#
#       Ref: https://www.django-rest-framework.org/api-guide/serializers/
#
# =================================================================================================
#    Date      Name                    Description of Change
# 13-Mar-2022  Wayne Shih              Initial create
# 19-Mar-2022  Wayne Shih              Add NotificationSerializerForUpdate
# $HISTORY$
# =================================================================================================


from django.contrib.auth.models import User
from rest_framework import serializers
from notifications.models import Notification

from accounts.api.serializers import UserSerializerForNotification
from comments.api.serializers import CommentSerializerForNotifications
from comments.models import Comment
from tweets.api.serializers import TweetSerializerForNotifications
from tweets.models import Tweet


class DefaultNotificationSerializer(serializers.Serializer):
    pass


class NotificationSerializer(serializers.ModelSerializer):
    actor = serializers.SerializerMethodField()
    target = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = (
            'id',
            'unread',
            'actor',
            'verb',
            'target',
            'timestamp',
        )

    def get_target(self, obj):
        if obj.target.__class__ == Tweet:
            return {'tweet': TweetSerializerForNotifications(obj.target).data}
        if obj.target.__class__ == Comment:
            return {'comment': CommentSerializerForNotifications(obj.target).data}
        return None

    def get_actor(self, obj):
        if obj.actor.__class__ == User:
            return {'user': UserSerializerForNotification(obj.actor).data}
        return None


class NotificationSerializerForUpdate(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = ('unread',)

    # <Wayne Shih> 18-Mar-2022
    # - https://www.django-rest-framework.org/api-guide/serializers/#saving-instances
    def update(self, instance, validated_data):
        instance.unread = validated_data['unread']
        instance.save()
        return instance
