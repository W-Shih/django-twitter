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
# 26-Feb-2021  Wayne Shih              Initial create
# $HISTORY$
# =================================================================================================


from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from accounts.api.serializers import UserSerializerForLike
from comments.models import Comment
from likes.models import Like
from tweets.models import Tweet


class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializerForLike()

    class Meta:
        model = Like
        fields = ('user', 'created_at')


class LikeSerializerForCreate(serializers.ModelSerializer):
    content_type = serializers.ChoiceField(choices=['tweet', 'comment'])

    class Meta:
        model = Like
        fields = ('content_type', 'object_id',)

    def _get_model_class(self, data):
        if data['content_type'] == 'tweet':
            return Tweet
        if data['content_type'] == 'comment':
            return Comment
        # <Wayne Shih> 26-Feb-2022
        # In fact, the code never comes here because serializers.ChoiceField() has
        # ensured that content_type must be either 'tweet' or 'comment'.
        return None

    def validate(self, data):
        model_class = self._get_model_class(data)
        if model_class is None:
            raise serializers.ValidationError({
                'content_type': 'Content type does not exist.'
            })
        if not model_class.objects.filter(id=data['object_id']).exists():
            raise serializers.ValidationError({
                'object_id': 'Object does not exist.'
            })
        return data

    # <Wayne Shih> 25-Feb-2022
    # - https://www.django-rest-framework.org/api-guide/serializers/#saving-instances
    # content_type is recorded in django_content_type table.
    # get_for_model() here is to get model's metadata so that db knows the model.
    # - https://docs.djangoproject.com/en/4.0/ref/contrib/contenttypes/#django.contrib.contenttypes.models.ContentTypeManager.get_for_model
    def create(self, validated_data):
        model_class = self._get_model_class(validated_data)
        like, _ = Like.objects.get_or_create(
            user_id=self.context['request'].user.id,
            content_type=ContentType.objects.get_for_model(model_class),
            object_id=validated_data['object_id'],
        )
        return like
