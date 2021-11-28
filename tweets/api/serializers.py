# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#       - Serializer for tweets api
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
# 06-Sep-2021  Wayne Shih              Initial create
# 10-Oct-2021  Wayne Shih              React to pylint checks
# 27-Nov-2021  Wayne Shih              Add TweetSerializerWithComments for tweet retrieve api
# 27-Nov-2021  Wayne Shih              Use SerializerMethodField instead to prefetch for comments
# $HISTORY$
# =================================================================================================


from rest_framework import serializers

from accounts.api.serializers import UserSerializerForTweet
from comments.api.serializers import CommentSerializer
from tweets.models import Tweet


class TweetSerializer(serializers.ModelSerializer):
    user = UserSerializerForTweet()

    class Meta:
        model = Tweet
        fields = ('id', 'user', 'created_at', 'content')


class TweetSerializerWithComments(TweetSerializer):
    # <Wayne Shih> 26-Nov-2021
    # - https://docs.djangoproject.com/en/3.2/topics/db/queries/#following-relationships-backward
    # - https://www.django-rest-framework.org/api-guide/fields/#using-source
    # It seems like source='comment_set' is not able to prefetch_related for comments
    # comments = CommentSerializer(source='comment_set', many=True)
    #
    # <Wayne Shih> 27-Nov-2021
    # Use SerializerMethodField instead in order to prefetch_related for comments
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Tweet
        fields = ('id', 'user', 'created_at', 'content', 'comments')

    def get_comments(self, obj):
        return CommentSerializer(
            obj.comment_set.all().prefetch_related('user'),
            many=True
        ).data


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
