# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#       - Serializer for friendships api
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
# 08-Sep-2021  Wayne Shih              Initial create
# 10-Oct-2021  Wayne Shih              React to pylint checks
# 27-Feb-2022  Wayne Shih              Add DefaultFriendshipSerializer
# 03-Apr-2022  Wayne Shih              Add has_followed to Follower and Following Serializers
# $HISTORY$
# =================================================================================================


from rest_framework import serializers

from accounts.api.serializers import UserSerializerForFriendship
from friendships.models import Friendship
from friendships.services import FriendshipService


class DefaultFriendshipSerializer(serializers.Serializer):
    pass


class FollowerSerializer(serializers.ModelSerializer):
    from_user = UserSerializerForFriendship()
    # user = UserSerializerForFriendship(source='from_user')
    has_followed = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ('from_user', 'created_at', 'has_followed')
        # fields = ('user', 'created_at',)

    def get_has_followed(self, obj):
        if self.context['request'].user.is_anonymous:
            return False

        # <Wayne Shih> 03-Apr-2022
        # TODO:
        #   Here causes N + 1 query problem, need to improve this by cache
        return FriendshipService.get_has_followed(
            from_user=self.context['request'].user,
            to_user=obj.from_user,
        )


class FollowingSerializer(serializers.ModelSerializer):
    # to_user = UserSerializerForFriendship()
    user = UserSerializerForFriendship(source='to_user')
    has_followed = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        # fields = ('to_user', 'created_at',)
        fields = ('user', 'created_at', 'has_followed')

    def get_has_followed(self, obj):
        if self.context['request'].user.is_anonymous:
            return False

        # <Wayne Shih> 03-Apr-2022
        # TODO:
        #   Here causes N + 1 query problem, need to improve this by cache
        return FriendshipService.get_has_followed(
            from_user=self.context['request'].user,
            to_user=obj.to_user,
        )


class FriendshipSerializerForCreate(serializers.ModelSerializer):
    from_user_id = serializers.IntegerField()
    to_user_id = serializers.IntegerField()

    class Meta:
        model = Friendship
        fields = ('from_user_id', 'to_user_id')

    def validate(self, data):
        if data['from_user_id'] == data['to_user_id']:
            raise serializers.ValidationError({
                'message': 'You can not follow yourself.'
            })
        return data

    def create(self, validated_data):
        friendship = Friendship.objects.create(
            from_user_id=validated_data['from_user_id'],
            to_user_id=validated_data['to_user_id'],
        )
        return friendship
