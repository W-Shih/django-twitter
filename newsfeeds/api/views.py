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
# $HISTORY$
# =================================================================================================


from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from newsfeeds.models import NewsFeed
from newsfeeds.api.serializers import NewsFeedSerializer


class NewsFeedViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return NewsFeed.objects.filter(user=self.request.user)

    # <Wayne Shih> 14-Sep-2021
    # - https://www.django-rest-framework.org/api-guide/viewsets/#marking-extra-actions-for-routing
    # @action(methods=['GET'], detail=False)
    # - To use @action, must specify detail
    # - @action can't apply on key word methods - list/retrieve/create/update/destroy
    def list(self, request):
        newsfeeds = self.get_queryset().order_by('-created_at')
        serializer = NewsFeedSerializer(newsfeeds, many=True, context={'request': request})
        return Response({
            'newsfeeds': serializer.data,
        }, status=status.HTTP_200_OK)
