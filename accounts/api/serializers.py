# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#       - Serializer for accounts api
#
#       - Serializers allow complex data such as querysets and model instances to be converted to
#         native Python datatypes that can then be easily rendered into JSON, XML or other content types.
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
# $HISTORY$
# =================================================================================================


from django.contrib.auth.models import User
from rest_framework import serializers, exceptions


class UserSerializer(serializers.ModelSerializer):
    # <Wayne Shih> 21-Aug-2021
    # Using ModelSerializers
    # - https://www.django-rest-framework.org/tutorial/1-serialization/#using-modelserializers
    class Meta:
        model = User
        fields = ('username', 'email')


class UserSerializerForTweet(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


# <Wayne Shih> 07-Aug-2021
# Ref: https://www.django-rest-framework.org/api-guide/serializers/#field-level-validatio
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


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
        # TODO<HOMEWORK> 增加验证 username 是不是只由给定的字符集合构成
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
        return user
