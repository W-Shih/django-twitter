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
# 26-Feb-2022  Wayne Shih              Initial create
# 05-Mar-2022  Wayne Shih              Add like cancel and list APIs
# $HISTORY$
# =================================================================================================


from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from likes.models import Like
from likes.api.serializers import (
    BaseLikeSerializerForCreateAndCancel,
    LikeSerializer,
    LikeSerializerForCancel,
    LikeSerializerForCreate,
)
from utils.decorators import required_params


class LikeViewSet(viewsets.GenericViewSet):
    queryset = Like.objects.all()
    serializer_class = BaseLikeSerializerForCreateAndCancel

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated()]

    def list(self, request):
        return Response({
            'message': {
                'Like tweet/comment': {
                    'method': 'POST',
                    'url': 'api/likes/',
                },
                'Unlike tweet/comment': {
                    'method': 'POST',
                    'url': '/api/likes/cancel/',
                },
            }
        }, status=status.HTTP_200_OK)

    # <Wayne Shih> 26-Feb-2022
    # URL:
    # - POST /api/likes/
    @required_params(method='POST', params=['content_type', 'object_id'])
    def create(self, request: Request):
        serializer = LikeSerializerForCreate(
            data=request.data,
            context={'request': request},
        )
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check input.',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        like = serializer.save()
        return Response(LikeSerializer(like).data, status=status.HTTP_201_CREATED)

    # <Wayne Shih> 05-Mar-2022
    # URL:
    # - POST /api/likes/cancel/
    @action(methods=['POST'], detail=False)
    @required_params(method='POST', params=['content_type', 'object_id'])
    def cancel(self, request: Request):
        serializer = LikeSerializerForCancel(
            data=request.data,
            context={'request': request},
        )
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check input.',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        num_deleted = serializer.cancel()
        return Response({
            'success': True,
            'num_deleted': num_deleted,
        }, status=status.HTTP_200_OK)
