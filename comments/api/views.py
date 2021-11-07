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
# 06-Nov-2021  Wayne Shih              Initial create
# $HISTORY$
# =================================================================================================


from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from comments.api.serializers import CommentSerializerForCreate, CommentSerializer


class CommentViewSet(viewsets.GenericViewSet):
    serializer_class = CommentSerializerForCreate
    permission_classes = [IsAuthenticated]

    # <Wayne Shih> 06-Nov-2021
    # URL:
    # - POST /api/comments/
    def create(self, request: Request):
        serializer = CommentSerializerForCreate(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check input.',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        comment = serializer.save()
        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)
