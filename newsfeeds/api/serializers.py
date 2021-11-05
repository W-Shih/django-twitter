# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#       - Serializer for newsfeed api
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
# 04-Nov-2021  Wayne Shih              Initial create
# $HISTORY$
# =================================================================================================


from rest_framework import serializers

from newsfeeds.models import NewsFeed
from tweets.api.serializers import TweetSerializer


class NewsFeedSerializer(serializers.ModelSerializer):
    tweet = TweetSerializer()

    class Meta:
        model = NewsFeed
        fields = ('id', 'user', 'created_at', 'tweet')
