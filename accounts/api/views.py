# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#       In other frameworks you may also find conceptually similar implementations named
#       something like 'Resources' or 'Controllers'.
#
#       Ref: https://www.django-rest-framework.org/api-guide/viewsets/
#
# =================================================================================================
#    Date      Name                    Description of Change
# 06-Aug-2021  Wayne Shih              Initial create
# 07-Aug-2021  Wayne Shih              Add AccountViewSet
# 21-Aug-2021  Wayne Shih              Use rest_framework.status instead and add some comments
# 21-Aug-2021  Wayne Shih              Add ip information in login_status for django-debug-toolbar
# 10-Oct-2021  Wayne Shih              React to pylint checks
# 27-Feb-2021  Wayne Shih              Enhance account api by decorator and GenericViewSet
# 23-Mar-2022  Wayne Shih              Add UserProfileViewSet
# $HISTORY$
# =================================================================================================


from django.contrib.auth import (
    authenticate as django_authenticate,
    login as django_login,
    logout as django_logout,
)
from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from accounts.api.serializers import (
    DefaultAccountSerializer,
    LoginSerializer,
    SignupSerializer,
    UserProfileSerializerForUpdate,
    UserSerializer,
)
from accounts.models import UserProfile
from utils.decorators import required_params
from utils.permissions import IsObjectOwner


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer  # the class to render the data to json
    # <Wayne Shih> 21-Aug-2021
    # Set permission_classes
    # - https://www.django-rest-framework.org/api-guide/permissions/#api-reference
    permission_classes = [permissions.IsAuthenticated]


# <Wayne Shih> 06-Aug-2021
# - Don't sub-class from ModelViewSet. It has read/write operations. This is dangerous!
# - Just sub-class from ViewSet. ViewSet has no read/write operations.
#   In this case, we need to write our own operations.
# - Django rest framework url pattern: /resource/action/
class AccountViewSet(viewsets.GenericViewSet):

    # <Wayne Shih> 27-Feb-2022
    # Once get_serializer_class() is implemented, then member data serializer_class will
    # not be used anymore. That is, serializer_class attribute is useless.
    def get_serializer_class(self):
        if self.action == 'signup':
            return SignupSerializer
        if self.action == 'login':
            return LoginSerializer
        return DefaultAccountSerializer

    def list(self, request):
        return Response({
            'message': {
                'Get login status': {
                    'method': 'GET',
                    'url': '/api/accounts/login_status/',
                },
                'Log out': {
                    'method': 'POST',
                    'url': '/api/accounts/logout/',
                },
                'Log in': {
                    'method': 'POST',
                    'url': 'api/accounts/login/',
                },
                'Sign up': {
                    'method': 'POST',
                    'url': '/api/accounts/signup/',
                },
            }
        }, status=status.HTTP_200_OK)

    # <Wayne Shih> 06-Aug-2021
    # - This operation maps /accounts/login_status
    # - detail refers to if this operation is on an specific resource obj
    #   If true, then this operation maps /accounts/{user_id}/login_status
    #   In this case, another argument pk needs to be passed in login_status()
    # - methods refer to a list of http actions that allow
    #   If an http action is not on the list, then it will return 405 - 'Method Not Allowed'
    @action(methods=['GET'], detail=False)
    def login_status(self, request):
        """
        Check current login status
        """
        # <Wayne Shih> 21-Aug-2021
        # 'django.contrib.auth.middleware.AuthenticationMiddleware' adds user attribute to request.
        # - https://docs.djangoproject.com/en/3.2/ref/middleware/#django.contrib.auth.middleware.AuthenticationMiddleware
        # - https://docs.djangoproject.com/en/3.2/ref/request-response/#attributes-set-by-middleware
        # is_authenticated is an attribute available on any subclass of AbstractBaseUser.
        # - https://docs.djangoproject.com/en/3.2/topics/auth/customizing/#django.contrib.auth.models.AbstractBaseUser
        data = {
            'has_logged_in': request.user.is_authenticated,
            'ip': request.META['REMOTE_ADDR'],
        }
        if request.user.is_authenticated:
            # <Wayne Shih> 21-Aug-2021
            # - Add 'user' attribute to data.
            # - UserSerializer converts request.user obj to json and store this converted json on
            #   its data attribute.
            # - https://www.django-rest-framework.org/api-guide/serializers/#serializing-objects
            data['user'] = UserSerializer(request.user).data

        # <Wayne Shih> 21-Aug-2021
        # Response(data) converts data to json and return.
        return Response(data)

    # <Wayne Shih> 06-Aug-2021
    # Ref: https://docs.djangoproject.com/en/3.0/topics/auth/default/#django.contrib.auth.logout
    @action(methods=['POST'], detail=False)
    @required_params(method='POST')
    def logout(self, request):
        """
        Logout current user
        """
        django_logout(request)
        return Response({'success': True})

    # <Wayne Shih> 07-Aug-2021
    # Ref:
    # - https://www.django-rest-framework.org/api-guide/serializers/#field-level-validation
    # - https://docs.djangoproject.com/en/3.2/topics/auth/default/#how-to-log-a-user-in
    # - https://docs.djangoproject.com/en/3.2/ref/contrib/auth/#attributes
    @action(methods=['POST'], detail=False)
    @required_params(method='POST', params=['username', 'password'])
    def login(self, request):
        """
        Login
        """
        # <Wayne Shih> 07-Aug-2021
        # get username and password from request
        # request.data returns the parsed content of the request body
        # - https://www.django-rest-framework.org/api-guide/requests/#data
        # Deserializing objects, validated_data, errors
        # - https://www.django-rest-framework.org/api-guide/serializers/#deserializing-objects
        # - https://www.django-rest-framework.org/api-guide/serializers/#validation
        # serializer = LoginSerializer(data=request.data)
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            # <Wayne Shih> 21-Aug-2021
            # Responses Signature
            # - https://www.django-rest-framework.org/api-guide/responses/#response
            return Response({
                'success': False,
                'message': 'Please check input.',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        # <Wayne Shih> 07-Aug-2021
        # If validation is OK, then get user
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        if not User.objects.filter(username=username).exists():
            # <Wayne Shih> 07-Aug-2021
            # If you would like to be more secure, then just let django_authenticate()
            # to handle this case and then response 'username and password does not match.'
            # to avoid someone trying to get usernames.
            # Try to print debug detail:
            # print(User.objects.filter(username=username).query)
            return Response({
                'success': False,
                'message': 'User does not exit.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # <Wayne Shih> 21-Aug-2021
        # login user
        # - https://docs.djangoproject.com/en/3.2/topics/auth/default/#how-to-log-a-user-in
        user = django_authenticate(username=username, password=password)
        if not user or user.is_anonymous:
            return Response({
                'success': False,
                'message': 'Username and password do not match.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # <Wayne Shih> 07-Aug-2021
        # If user got, login
        django_login(request, user)

        # <Wayne Shih> 21-Aug-2021
        # _serializerObj.data is json
        # - https://www.django-rest-framework.org/api-guide/serializers/#serializing-objects
        return Response({
            'success': True,
            'user': UserSerializer(user).data
        })

    @action(methods=['POST'], detail=False)
    @required_params(method='POST', params=['username', 'password'])
    def signup(self, request):
        """
        Give username, email, password to sign up a new user
        """
        # <Wayne Shih> 07-Aug-2021
        # get post data
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check input.',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        # <Wayne Shih> 07-Aug-2021
        # If data got, create a new user and login.
        # If we want to be able to return complete object instances based on the validated data,
        # we need to implement one or both of .create() and .update() methods in serializer.
        # - https://www.django-rest-framework.org/api-guide/serializers/#saving-instances
        # This new created user is authenticated.
        user = serializer.save()

        # <Wayne Shih> 21-Aug-2021
        # login user
        # - https://docs.djangoproject.com/en/3.2/topics/auth/default/#how-to-log-a-user-in
        django_login(request, user)
        return Response({
            'success': True,
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class UserProfileViewSet(viewsets.GenericViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializerForUpdate

    def get_permissions(self):
        if self.action == 'update':
            return [IsAuthenticated(), IsObjectOwner()]
        return [AllowAny()]

    def list(self, request):
        return Response({
            'message': {
                'Update profile': {
                    'method': 'PUT',
                    'url': '/api/profiles/{profile_id_pk}/',
                },
            }
        }, status=status.HTTP_200_OK)

    # <Wayne Shih> 22-Mar-2022
    # URL:
    # - PUT /api/profiles/{pk}/
    # Typically use PUT to perform partial update.
    @required_params(method='PUT', params=['nickname', 'avatar'], is_required_all=False)
    def update(self, request, *args, **kwargs):
        profile = self.get_object()
        serializer = self.get_serializer(instance=profile, data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check input.',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        profile = serializer.save()
        return Response(
            UserProfileSerializerForUpdate(profile).data,
            status=status.HTTP_200_OK,
        )
