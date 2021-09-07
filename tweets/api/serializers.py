# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#       - Serializer for tweets api
#
#       - Serializers allow complex data such as querysets and model instances to be converted to
#         native Python datatypes that can then be easily rendered into JSON, XML or other content types.
#       - Can be used as a validator to validate if request is valid
#
#       Ref: https://www.django-rest-framework.org/api-guide/serializers/
#
# =================================================================================================
#    Date      Name                    Description of Change
# 06-Sep-2021  Wayne Shih              Initial create
# $HISTORY$
# =================================================================================================


from accounts.api.serializers import UserSerializerForTweet
from rest_framework import serializers
from tweets.models import Tweet


class TweetSerializer(serializers.ModelSerializer):
    user = UserSerializerForTweet()

    class Meta:
        model = Tweet
        fields = ('id', 'user', 'created_at', 'content')


class TweetSerializerForCreate(serializers.ModelSerializer):
    content = serializers.CharField(min_length=6, max_length=255)

    class Meta:
        model = Tweet
        fields = ('content',)

    # <Wayne Shih> 06-Sep-2021
    # - https://www.django-rest-framework.org/api-guide/serializers/#saving-instances
    def create(self, validated_data):
        user_id = self.context['request'].user.id
        content = validated_data['content']
        tweet = Tweet.objects.create(user_id=user_id, content=content)
        return tweet

