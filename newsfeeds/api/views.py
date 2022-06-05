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
# 04-Nov-2021  Wayne Shih              Initial create
# 12-Mar-2022  Wayne Shih              React to tweet serializer changes
# 27-Apr-2022  Wayne Shih              Add endless pagination for newsfeed list api
# 29-Apr-2022  Wayne Shih              Deprecate key in newsfeeds list api
# 30-May-2022  Wayne Shih              React to user newsfeeds cache
# 05-Jun-2022  Wayne Shih              React to only caching REDIS_LIST_SIZE_LIMIT in redis
# $HISTORY$
# =================================================================================================


from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from newsfeeds.api.serializers import NewsFeedSerializer
from newsfeeds.models import NewsFeed
from newsfeeds.services import NewsFeedService
from utils.pagination import EndlessPagination


class NewsFeedViewSet(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    pagination_class = EndlessPagination

    def get_queryset(self):
        return NewsFeed.objects.filter(user=self.request.user)

    # <Wayne Shih> 14-Sep-2021
    # - https://www.django-rest-framework.org/api-guide/viewsets/#marking-extra-actions-for-routing
    # @action(methods=['GET'], detail=False)
    # - To use @action, must specify detail
    # - @action can't apply on key word methods - list/retrieve/create/update/destroy
    def list(self, request):
        cached_newsfeeds = NewsFeedService.get_cached_newsfeeds(request.user.id)
        page = self.paginator.paginate_cached_list(cached_newsfeeds, request)
        if page is None:
            newsfeeds = self.get_queryset().order_by('-created_at')
            page = self.paginate_queryset(newsfeeds)
        serializer = NewsFeedSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)
