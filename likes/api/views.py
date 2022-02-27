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
# $HISTORY$
# =================================================================================================


from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from likes.models import Like
from likes.api.serializers import LikeSerializer, LikeSerializerForCreate
from utils.decorators import required_params


class LikeViewSet(viewsets.GenericViewSet):
    queryset = Like.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = LikeSerializerForCreate

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
