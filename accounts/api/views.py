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
# $HISTORY$
# =================================================================================================


from django.contrib.auth import (
    authenticate as django_authenticate,
    login as django_login,
    logout as django_logout,
)
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.api.serializers import (
    LoginSerializer,
    SignupSerializer,
    UserSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer # the class to render the data to json
    permission_classes = [permissions.IsAuthenticated]


class AccountViewSet(viewsets.ViewSet):
    """
    API endpoint that allows to see user's login_status
    """
    # <Wayne Shih> 06-Aug-2021
    # - Don't sub-class from ModelViewSet. It has read/write operations. This is dangerous!
    # - Just sub-class from ViewSet. ViewSet has no read/write operations.
    #   In this case, we need to write our own operations.
    # - Django rest framework url pattern: /resource/action/

    serializer_class = SignupSerializer

    # <Wayne Shih> 06-Aug-2021
    # - This operation maps /accounts/login_status
    # - detail refers to if this operation is on an specific resource obj
    #   If true, then this operation maps /accounts/{user_id}/login_status
    #   In this case, another argument pk needs to be passed in login_status()
    # - methods refer to a list of http actions that allow
    #   If an http action is not on the list, then it will return 405 - 'Method Not Allowed'
    @action(methods=['GET'], detail=False)
    def login_status(self, request):
        data = {'has_logged_in': request.user.is_authenticated}
        if request.user.is_authenticated:
            data['user'] = UserSerializer(request.user).data
        return Response(data)

    # <Wayne Shih> 06-Aug-2021
    # Ref: https://docs.djangoproject.com/en/3.0/topics/auth/default/#django.contrib.auth.logout
    @action(methods=['POST'], detail=False)
    def logout(self, request):
        django_logout(request)
        return Response({'success': True})

    # <Wayne Shih> 07-Aug-2021
    # Ref:
    # - https://www.django-rest-framework.org/api-guide/serializers/#field-level-validation
    # - https://docs.djangoproject.com/en/3.2/topics/auth/default/#how-to-log-a-user-in
    # - https://docs.djangoproject.com/en/3.2/ref/contrib/auth/#attributes
    @action(methods=['POST'], detail=False)
    def login(self, request):
        # <Wayne Shih> 07-Aug-2021
        # get username and password from request
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check input.',
                'errors': serializer.errors,
            }, status=400)

        # <Wayne Shih> 07-Aug-2021
        # If validation is OK, then get user
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        if not User.objects.filter(username=username).exists():
            # <Wayne Shih> 07-Aug-2021
            # If you would like to be more secure, then just response 'username and password does not match.'
            # to avoid someone trying to get usernames.
            # Try to print debug detail:
            # print(User.objects.filter(username=username).query)
            return Response({
                'success': False,
                'message': 'User does not exit.'
            }, status=400)

        user = django_authenticate(username=username, password=password)
        if not user or user.is_anonymous:
            return Response({
                'success': False,
                'message': 'Username and password does not match.'
            }, status=400)

        # <Wayne Shih> 07-Aug-2021
        # If user got, login
        django_login(request, user)
        return Response({
            'success': True,
            'user': UserSerializer(user).data
        })

    @action(methods=['POST'], detail=False)
    def signup(self, request):
        # <Wayne Shih> 07-Aug-2021
        # get post data
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check input.',
                'errors': serializer.errors,
            }, status=400)

        # <Wayne Shih> 07-Aug-2021
        # If data got, create a new user and login
        user = serializer.save()
        django_login(request, user)
        return Response({
            'success': True,
            'user': UserSerializer(user).data
        }, status=201)

