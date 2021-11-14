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
# 13-Nov-2021  Wayne Shih              Add comments update and destroy apis
# $HISTORY$
# =================================================================================================


from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from comments.api.permissions import IsObjectOwner
from comments.api.serializers import (
    CommentSerializer,
    CommentSerializerForCreate,
    CommentSerializerForUpdate,
)
from comments.models import Comment


class CommentViewSet(viewsets.GenericViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializerForCreate
    # <Wayne Shih> 13-Nov-2021
    # TODO:
    #   This permission_classes might be not not suitable when retrieve api is considered.
    permission_classes = [IsAuthenticated, IsObjectOwner]

    # <Wayne Shih> 06-Nov-2021
    # URL:
    # - POST /api/comments/
    def create(self, request: Request):
        data = {
            'user_id': request.user.id,
            'tweet_id': request.data.get('tweet_id'),
            'content': request.data.get('content'),
        }
        serializer = CommentSerializerForCreate(data=data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check input.',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        comment = serializer.save()
        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)

    # <Wayne Shih> 08-Nov-2021
    # URL:
    # - DELETE /api/comments/{pk}/
    def destroy(self, request: Request, *args, **kwargs):
        comment = self.get_object()
        num_deleted, _ = comment.delete()
        return Response({
            'success': num_deleted == 1
        }, status=status.HTTP_200_OK)

    # <Wayne Shih> 08-Nov-2021
    # URL:
    # - PUT /api/comments/{pk}/
    # Typically use PUT to perform partial update.
    def update(self, request, *args, **kwargs):
        comment = self.get_object()
        data = {'content': request.data.get('content')}
        serializer = CommentSerializerForUpdate(instance=comment, data=data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check input.',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(CommentSerializer(comment).data, status=status.HTTP_200_OK)
