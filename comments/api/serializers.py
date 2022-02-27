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
# $HISTORY$
# =================================================================================================


from rest_framework import serializers

from accounts.api.serializers import UserSerializerForComment
from comments.models import Comment
from tweets.models import Tweet


class DefaultCommentSerializer(serializers.Serializer):
    pass


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializerForComment()

    class Meta:
        model = Comment
        fields = ('id', 'tweet_id', 'user', 'content', 'created_at')


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
