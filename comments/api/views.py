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
# 25-Nov-2021  Wayne Shih              Add comments list api
# 25-Nov-2021  Wayne Shih              Enhance comments list api by dango-filters
# 25-Nov-2021  Wayne Shih              Enhance comments list api by prefetch_related/select_related
# 27-Nov-2021  Wayne Shih              Enhance comments list api by decorator
# $HISTORY$
# =================================================================================================


from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from comments.api.permissions import IsObjectOwner
from comments.api.serializers import (
    CommentSerializer,
    CommentSerializerForCreate,
    CommentSerializerForUpdate,
)
from comments.models import Comment
from utils.decorators import required_params


class CommentViewSet(viewsets.GenericViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializerForCreate
    filterset_fields = ('tweet_id', 'user_id')

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        if self.action in ['update', 'destroy']:
            return [IsAuthenticated(), IsObjectOwner()]
        return [AllowAny()]

    # <Wayne Shih> 25-Nov-2021
    # django-filter
    # - https://www.django-rest-framework.org/api-guide/filtering/
    #
    # URL:
    # - GET /api/comments/?tweet_id=1 -> Get all comments related to a given tweet
    # - GET /api/comments/?user_id=1 -> Get all comments related to a given user
    @required_params(params=['tweet_id', 'user_id'], is_required_all=False)
    def list(self, request: Request):
        queryset = self.get_queryset()
        # <Wayne Shih> 25-Nov-2021
        # prefetch_related <-> SQL SELECT in query
        # select_related <-> SQL SELECT JOIN
        # JOIN is not recommended because JOIN only works in the same database.
        # If these user and comment are not in the same db, then JOIN will NOT work.
        # comments = self.filter_queryset(queryset).select_related('user').order_by('created_at')
        comments = self.filter_queryset(queryset)\
            .prefetch_related('user')\
            .order_by('created_at')

        return Response({
            'comments': CommentSerializer(comments, many=True).data,
        }, status=status.HTTP_200_OK)

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
