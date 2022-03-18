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
# 13-Mar-2022  Wayne Shih              Initial create
# $HISTORY$
# =================================================================================================


from notifications.models import Notification
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from inbox.api.serializers import NotificationSerializer, DefaultNotificationSerializer


class NotificationViewSet(viewsets.GenericViewSet):
    queryset = Notification.objects.all()
    serializer_class = DefaultNotificationSerializer
    permission_classes = (IsAuthenticated,)
    # <Wayne Shih> 15-Mar-2022
    # filterset_fields is a shortcut for filterset_class
    # https://django-filter.readthedocs.io/en/latest/guide/rest_framework.html#adding-a-filterset-with-filterset-class
    # https://django-filter.readthedocs.io/en/latest/guide/rest_framework.html#using-the-filterset-fields-shortcut
    filterset_fields = ('unread',)

    # <Wayne Shih> 13-Mar-2022
    # URL:
    # - GET /api/notifications/
    def list(self, request: Request):
        queryset = self.get_queryset()
        notifications = self.filter_queryset(queryset)\
            .filter(recipient=request.user)\
            .order_by('-timestamp')\
            .prefetch_related('actor', 'target')
        serializer = NotificationSerializer(notifications, many=True, context={'request': request})
        return Response({
            'notifications': serializer.data,
        }, status=status.HTTP_200_OK)

    # <Wayne Shih> 13-Mar-2022
    # URL:
    # - GET /api/notifications/unread-count/
    @action(methods=['GET'], detail=False, url_path='unread-count')
    def unread_count(self, request: Request):
        queryset = self.get_queryset()
        unread_count = queryset.filter(recipient=request.user, unread=True).count()
        return Response({'unread_count': unread_count}, status=status.HTTP_200_OK)

    # <Wayne Shih> 13-Mar-2022
    # URL:
    # - POST /api/notifications/mark-all-as-read/
    @action(methods=['POST'], detail=False, url_path='mark-all-as-read')
    def mark_all_as_read(self, request: Request):
        queryset = self.get_queryset()
        # <Wayne Shih> 13-Mar-2022
        # queryset has its own update() method
        # https://docs.djangoproject.com/en/4.0/ref/models/querysets/#django.db.models.query.QuerySet.update
        num_updated = queryset.filter(recipient=request.user, unread=True).update(unread=False)
        return Response({'marked_count': num_updated}, status=status.HTTP_200_OK)
