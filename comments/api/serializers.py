# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#       - Serializer for comments api
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
# 06-Nov-2021  Wayne Shih              Initial create
# 13-Nov-2021  Wayne Shih              Add CommentSerializerForUpdate and some comments
# 27-Feb-2022  Wayne Shih              Enhance CommentSerializerForCreate() and add DefaultCommentSerializer
# 12-Mar-2022  Wayne Shih              Insert likes_count and has_liked to comment serializer
# 17-Mar-2022  Wayne Shih              Add CommentSerializerForNotifications
# 26-May-2022  Wayne Shih              Fetch user from cache
# 11-Jun-2022  Wayne Shih              Fetch likes_count from cache
# $HISTORY$
# =================================================================================================


from rest_framework import serializers

from accounts.api.serializers import UserSerializerForComment
from comments.models import Comment
from likes.services import LikeService
from tweets.models import Tweet
from utils.caches.redis_helpers import RedisHelper


class DefaultCommentSerializer(serializers.Serializer):
    pass


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializerForComment(source='cached_user')
    likes_count = serializers.SerializerMethodField()
    has_liked = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            'id',
            'tweet_id',
            'user',
            'content',
            'created_at',
            'likes_count',
            'has_liked',
        )

    def get_likes_count(self, obj):
        return RedisHelper.get_count(obj, 'likes_count')

    def get_has_liked(self, obj):
        return LikeService.get_has_liked(self.context['request'].user, obj)


class CommentSerializerForCreate(serializers.ModelSerializer):
    tweet_id = serializers.IntegerField()

    class Meta:
        model = Comment
        fields = ('tweet_id', 'content',)

    def validate(self, data):
        if not Tweet.objects.filter(id=data['tweet_id']).exists():
            raise serializers.ValidationError({
                'tweet_id': 'tweet does not exist.'
            })
        return data

    # <Wayne Shih> 06-Nov-2021
    # - https://www.django-rest-framework.org/api-guide/serializers/#saving-instances
    def create(self, validated_data):
        comment = Comment.objects.create(
            user_id=self.context['request'].user.id,
            tweet_id=validated_data['tweet_id'],
            content=validated_data['content'],
        )
        return comment


class CommentSerializerForUpdate(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('content',)

    # <Wayne Shih> 11-Nov-2021
    # - https://www.django-rest-framework.org/api-guide/serializers/#saving-instances
    def update(self, instance, validated_data):
        instance.content = validated_data['content']
        instance.save()
        return instance


class CommentSerializerForNotifications(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = (
            'id',
            'tweet_id',
            'content',
            'created_at',
        )
