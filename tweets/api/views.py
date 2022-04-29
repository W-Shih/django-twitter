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
# 06-Sep-2021  Wayne Shih              Initial create
# 10-Oct-2021  Wayne Shih              React to pylint checks
# 18-Oct-2021  Wayne Shih              Add newsfeeds fanout to followers
# 27-Nov-2021  Wayne Shih              Add retrieve api
# 27-Nov-2021  Wayne Shih              Enhance api by prefetch_related and decorator
# 23-Feb-2022  Wayne Shih              Add TODO: to enhance list api by django-filters
# 27-Feb-2021  Wayne Shih              Enhance api by decorator
# 12-Mar-2022  Wayne Shih              React to serializer changes
# 26-Apr-2022  Wayne Shih              Add endless pagination for list api
# 27-Apr-2022  Wayne Shih              React to renaming to EndlessPagination
# 29-Apr-2022  Wayne Shih              Fix query string bug for list api
# 29-Apr-2022  Wayne Shih              Deprecate key in tweets list api
# $HISTORY$
# =================================================================================================


import django_filters

from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from newsfeeds.services import NewsFeedService
from tweets.api.serializers import (
    TweetSerializer,
    TweetSerializerForCreate,
    TweetSerializerForDetail,
)
from tweets.models import Tweet
from utils.pagination import EndlessPagination
from utils.decorators import required_params


class TweetFilter(django_filters.rest_framework.FilterSet):
    # https://www.django-rest-framework.org/api-guide/filtering/#overriding-the-initial-queryset
    # https://django-filter.readthedocs.io/en/latest/guide/rest_framework.html#adding-a-filterset-with-filterset-class
    # https://q1mi.github.io/Django-REST-framework-documentation/api-guide/filtering_zh/#specifying-a-filtersetfilterset
    user_id = django_filters.NumberFilter(field_name='user_id')

    class Meta:
        model = Tweet
        fields = ('user_id',)


class TweetViewSet(viewsets.GenericViewSet):
    # <Wayne Shih> 06-Sep-2021
    # rest_framework will use serializer_class to be the POST format at the rest page
    # - https://www.django-rest-framework.org/api-guide/generic-views/#genericapiview
    serializer_class = TweetSerializerForCreate
    # <Wayne Shih> 27-Nov-2021
    # TODO:
    #   prefetch_related for comments
    queryset = Tweet.objects.all().prefetch_related('user')
    filterset_class = TweetFilter
    pagination_class = EndlessPagination

    # <Wayne Shih> 06-Sep-2021
    # - https://www.django-rest-framework.org/api-guide/viewsets/#introspecting-viewset-actions
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    # <Wayne Shih> 26-Nov-2021
    # URL:
    # - GET /api/tweets/{pk}/
    def retrieve(self, request: Request, *args, **kwargs):
        tweet = self.get_object()
        serializer = TweetSerializerForDetail(tweet, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    # <Wayne Shih> 06-Sep-2021
    # URL:
    # - GET /api/tweets/?user_id=1 --> OK
    # - GET /api/tweets/ --> Not OK
    # - https://www.django-rest-framework.org/api-guide/viewsets/#viewset-actions
    # - https://www.django-rest-framework.org/api-guide/viewsets/#genericviewset
    # - https://www.django-rest-framework.org/api-guide/viewsets/#example
    @required_params(params=['user_id'])
    def list(self, request: Request):
        tweets = self.filter_queryset(self.get_queryset()).prefetch_related('user')
        # print('--- sql --- \n{}'.format(tweets.query))
        page = self.paginate_queryset(tweets)
        serializer = TweetSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    # <Wayne Shih> 06-Sep-2021
    # URL:
    # - POST /api/tweets/
    @required_params(method='POST', params=['content'])
    def create(self, request: Request):
        serializer = TweetSerializerForCreate(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check input.',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        # <Wayne Shih> 06-Sep-2021
        # - https://www.django-rest-framework.org/api-guide/serializers/#saving-instances
        tweet = serializer.save()
        NewsFeedService.fanout_to_followers(tweet)
        return Response(
            TweetSerializer(tweet, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )
