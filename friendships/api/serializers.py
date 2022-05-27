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
# 30-Apr-2022  Wayne Shih              Resolve N + 1 query problem by cache
# 26-May-2022  Wayne Shih              Fetch user from cache
# $HISTORY$
# =================================================================================================


from rest_framework import serializers

from accounts.api.serializers import UserSerializerForFriendship
from friendships.models import Friendship
from friendships.services import FriendshipService


class FollowingUserIdSetMixin:
    @property
    def following_user_id_set(self: serializers.ModelSerializer):
        if self.context['request'].user.is_anonymous:
            return {}
        if hasattr(self, '_cached_following_user_id_set'):
            return self._cached_following_user_id_set
        following_user_id_set = FriendshipService.get_following_user_id_set(
            from_user_id=self.context['request'].user.id,
        )
        setattr(self, '_cached_following_user_id_set', following_user_id_set)
        return following_user_id_set


class DefaultFriendshipSerializer(serializers.Serializer):
    pass


class FollowerSerializer(serializers.ModelSerializer, FollowingUserIdSetMixin):
    from_user = UserSerializerForFriendship(source='cached_from_user')
    # user = UserSerializerForFriendship(source='from_user')
    has_followed = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ('from_user', 'created_at', 'has_followed')
        # fields = ('user', 'created_at',)

    def get_has_followed(self, obj):
        if self.context['request'].user.is_anonymous:
            return False
        return obj.from_user.id in self.following_user_id_set


class FollowingSerializer(serializers.ModelSerializer, FollowingUserIdSetMixin):
    # to_user = UserSerializerForFriendship()
    user = UserSerializerForFriendship(source='cached_to_user')
    has_followed = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        # fields = ('to_user', 'created_at',)
        fields = ('user', 'created_at', 'has_followed')

    def get_has_followed(self, obj):
        if self.context['request'].user.is_anonymous:
            return False
        return obj.to_user.id in self.following_user_id_set


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
