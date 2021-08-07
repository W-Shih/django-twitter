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


from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.api.serializers import UserSerializer


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

    # <Wayne Shih> 06-Aug-2021
    # - This operation maps /accounts/login_status
    # - detail refers to if this operation is on an specific resource obj
    #   If true, then this operation maps /accounts/{user_id}/login_status
    #   In this case, another argument pk needs to be passed in login_status()
    @action(methods=['GET'], detail=False)
    def login_status(self, request):
        data = {'has_logged_in': request.user.is_authenticated}
        if request.user.is_authenticated:
            data['user'] = UserSerializer(request.user).data
        return Response(data)


