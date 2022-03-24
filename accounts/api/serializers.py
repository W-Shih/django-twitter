# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#       - Serializer for accounts api
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
# 06-Aug-2021  Wayne Shih              Initial create
# 07-Aug-2021  Wayne Shih              Add LoginSerializer and SignupSerializer
# 21-Aug-2021  Wayne Shih              Modify SignupSerializer.validate and add some comments
# 06-Sep-2021  Wayne Shih              Add UserSerializerForTweet
# 12-Sep-2021  Wayne Shih              Add UserSerializerForFriendship
# 10-Oct-2021  Wayne Shih              React to pylint checks
# 05-Nov-2021  Wayne Shih              Update TODO
# 06-Nov-2021  Wayne Shih              Add UserSerializerForComment
# 26-Feb-2022  Wayne Shih              Add UserSerializerForLike
# 27-Feb-2022  Wayne Shih              Add DefaultAccountSerializer
# 17-Mar-2022  Wayne Shih              Add UserSerializerForNotification
# 20-Mar-2022  Wayne Shih              Create user's profile right after user has been created
# 23-Mar-2022  Wayne Shih              Update user-related serializer and add UserProfileSerializerForUpdate
# $HISTORY$
# =================================================================================================


from django.contrib.auth.models import User
from rest_framework import exceptions, serializers

from accounts.models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    # <Wayne Shih> 21-Aug-2021
    # Using ModelSerializers
    # - https://www.django-rest-framework.org/tutorial/1-serialization/#using-modelserializers
    class Meta:
        model = User
        fields = ('id', 'username')


class UserSerializerWithProfile(serializers.ModelSerializer):
    nickname = serializers.CharField(source='profile.nickname')
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'nickname', 'avatar_url')

    def get_avatar_url(self, obj):
        if obj.profile.avatar:
            return obj.profile.avatar.url
        return None


class UserSerializerForTweet(UserSerializerWithProfile):
    pass


class UserSerializerForFriendship(UserSerializerWithProfile):
    pass


class UserSerializerForComment(UserSerializerWithProfile):
    pass


class UserSerializerForLike(UserSerializerWithProfile):
    pass


class UserSerializerForNotification(UserSerializerWithProfile):
    pass


# <Wayne Shih> 07-Aug-2021
# Ref: https://www.django-rest-framework.org/api-guide/serializers/#field-level-validatio
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class DefaultAccountSerializer(serializers.Serializer):
    pass


# <Wayne Shih> 07-Aug-2021
# Sub-classing from ModelSerializer to create/update a data when save() is called.
class SignupSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=20, min_length=6)
    password = serializers.CharField(max_length=20, min_length=6)
    email = serializers.EmailField()

    # <Wayne Shih> 07-Aug-2021
    # Assign User model and fields.
    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    # <Wayne Shih> 07-Aug-2021
    # Will be called when is_valid is called.
    # - https://www.django-rest-framework.org/api-guide/serializers/#object-level-validation
    # Default validate() only checks if name and type.
    # We overwrite this method to make it not case-sensitive.
    def validate(self, data):
        # <Wayne Shih> 05-Nov-2021
        # TODO:
        #   Add checking if username only includes certain given chars
        if User.objects.filter(username=data['username'].lower()).exists():
            raise exceptions.ValidationError({
                'username': 'This username has been occupied.'
            })
        if User.objects.filter(email=data['email'].lower()).exists():
            raise exceptions.ValidationError({
                'email': 'This email address has been occupied.'
            })
        return data

    # <Wayne Shih> 07-Aug-2021
    # Need to implement create() method, which is an abstract method.
    # Will be called save() is called.
    # - https://www.django-rest-framework.org/api-guide/serializers/#saving-instances
    # To create a user, underneath we save all lower cases for username and email
    # in order to make validation efficient.
    def create(self, validated_data):
        username = validated_data['username'].lower()
        email = validated_data['email'].lower()
        password = validated_data['password']

        # <Wayne Shih> 07-Aug-2021
        # create_user() is a specific method of User model.
        # It will underneath make 'true' password to a hashed password
        # In general cases, other models use create() to create new data
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        # <Wayne Shih> 19-Mar-2022
        # Create user's profile right after user has been created
        user.profile
        return user


class UserProfileSerializerForUpdate(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('nickname', 'avatar')
