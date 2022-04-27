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
# $HISTORY$
# =================================================================================================


from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from newsfeeds.models import NewsFeed
from newsfeeds.api.serializers import NewsFeedSerializer
from utils.pagination import EndlessPagination


class NewsFeedViewSet(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    pagination_class = EndlessPagination

    # <Wayne Shih> 27-Apr-2022
    # TODO:
    #   Remove this method after front-end & app-end deprecate keys 'newsfeeds'.
    def _get_paginated_response(self, data, deprecated_key=None):
        assert self.paginator is not None
        if not deprecated_key:
            return self.paginator.get_paginated_response(data)
        return self.paginator.get_customized_paginated_response(data, deprecated_key)

    def get_queryset(self):
        return NewsFeed.objects.filter(user=self.request.user)

    # <Wayne Shih> 14-Sep-2021
    # - https://www.django-rest-framework.org/api-guide/viewsets/#marking-extra-actions-for-routing
    # @action(methods=['GET'], detail=False)
    # - To use @action, must specify detail
    # - @action can't apply on key word methods - list/retrieve/create/update/destroy
    def list(self, request):
        newsfeeds = self.get_queryset().order_by('-created_at')
        page = self.paginate_queryset(newsfeeds)
        serializer = NewsFeedSerializer(page, many=True, context={'request': request})
        # <Wayne Shih> 27-Apr-2022
        # TODO:
        #   Remove key 'newsfeeds' after front-end & app-end deprecate it.
        return self._get_paginated_response(serializer.data, 'newsfeeds')
