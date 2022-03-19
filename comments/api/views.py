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
# 25-Nov-2021  Wayne Shih              Enhance comments list api by django-filters
# 25-Nov-2021  Wayne Shih              Enhance comments list api by prefetch_related/select_related
# 27-Nov-2021  Wayne Shih              Enhance comments list api by decorator
# 23-Feb-2022  Wayne Shih              Enhance comments list api by django-filters: filterset_class
# 24-Feb-2022  Wayne Shih              Fix pylint
# 27-Feb-2021  Wayne Shih              Enhance api by decorator and get_serializer_class()
# 12-Mar-2022  Wayne Shih              React to serializer changes
# 12-Mar-2022  Wayne Shih              Trigger notification when create a comment
# 19-Mar-2022  Wayne Shih              React to permissions.py refactor
# $HISTORY$
# =================================================================================================


import django_filters

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from comments.api.serializers import (
    CommentSerializer,
    CommentSerializerForCreate,
    CommentSerializerForUpdate,
    DefaultCommentSerializer,
)
from comments.models import Comment
from inbox.services import NotificationService
from utils.decorators import required_params
from utils.permissions import IsObjectOwner


class CommentFilter(django_filters.rest_framework.FilterSet):
    # https://www.django-rest-framework.org/api-guide/filtering/#overriding-the-initial-queryset
    # https://django-filter.readthedocs.io/en/latest/guide/rest_framework.html#adding-a-filterset-with-filterset-class
    # https://q1mi.github.io/Django-REST-framework-documentation/api-guide/filtering_zh/#specifying-a-filtersetfilterset
    tweet_id = django_filters.NumberFilter(field_name='tweet_id')
    user_id = django_filters.NumberFilter(field_name='user_id')

    class Meta:
        model = Comment
        fields = ('tweet_id', 'user_id')


class CommentViewSet(viewsets.GenericViewSet):
    queryset = Comment.objects.all()
    filterset_class = CommentFilter

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        if self.action in ['update', 'destroy']:
            return [IsAuthenticated(), IsObjectOwner()]
        return [AllowAny()]

    def get_serializer_class(self):
        if self.action == 'create':
            return CommentSerializerForCreate
        if self.action == 'update':
            return CommentSerializerForUpdate
        return DefaultCommentSerializer

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
        serializer = CommentSerializer(comments, many=True, context={'request': request})

        return Response({
            'comments': serializer.data,
        }, status=status.HTTP_200_OK)

    # <Wayne Shih> 06-Nov-2021
    # URL:
    # - POST /api/comments/
    @required_params(method='POST', params=['tweet_id', 'content'])
    def create(self, request: Request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check input.',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        comment = serializer.save()
        NotificationService.send_comment_notification(comment)
        return Response(
            CommentSerializer(comment, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )

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
    @required_params(method='PUT', params=['content'])
    def update(self, request, *args, **kwargs):
        comment = self.get_object()
        data = {'content': request.data.get('content')}
        serializer = self.get_serializer(instance=comment, data=data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check input.',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        comment = serializer.save()
        return Response(
            CommentSerializer(comment, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )
