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
# 19-Mar-2022  Wayne Shih              Add notifications update api
# 19-Mar-2022  Wayne Shih              Update notifications list api by ListModelMixin
# 18-Jun-2022  Wayne Shih              Add ratelimit
# $HISTORY$
# =================================================================================================


from django.utils.decorators import method_decorator
from notifications.models import Notification
from ratelimit.decorators import ratelimit
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from inbox.api.serializers import (
    DefaultNotificationSerializer,
    NotificationSerializer,
    NotificationSerializerForUpdate,
)
from utils.decorators import required_params
from utils.permissions import IsObjectOwner


class NotificationViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.ListModelMixin,
):
    permission_classes = (IsAuthenticated, IsObjectOwner,)
    # <Wayne Shih> 15-Mar-2022
    # filterset_fields is a shortcut for filterset_class
    # https://django-filter.readthedocs.io/en/latest/guide/rest_framework.html#adding-a-filterset-with-filterset-class
    # https://django-filter.readthedocs.io/en/latest/guide/rest_framework.html#using-the-filterset-fields-shortcut
    filterset_fields = ('unread',)

    def get_queryset(self):
        if self.action == 'list':
            return Notification.objects\
                .filter(recipient=self.request.user)\
                .order_by('-timestamp')\
                .prefetch_related('actor', 'target')
        if self.action == 'update':
            return Notification.objects.all()
        return Notification.objects.filter(recipient=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return NotificationSerializer
        if self.action == 'update':
            return NotificationSerializerForUpdate
        return DefaultNotificationSerializer

    # <Wayne Shih> 18-Mar-2022
    # URL:
    # - PUT /api/notifications/{pk}/
    # Typically use PUT to perform partial update.
    @required_params(method='PUT', params=['unread'])
    @method_decorator(ratelimit(key='user_or_ip', rate='3/s', method='PUT', block=True))
    def update(self, request, *args, **kwargs):
        notification = self.get_object()
        serializer = self.get_serializer(instance=notification, data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check input.',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        notification = serializer.save()
        return Response(
            NotificationSerializer(notification).data,
            status=status.HTTP_200_OK,
        )

    # <Wayne Shih> 13-Mar-2022
    # URL:
    # - GET /api/notifications/unread-count/
    @action(methods=['GET'], detail=False, url_path='unread-count')
    @method_decorator(ratelimit(key='user_or_ip', rate='3/s', method='GET', block=True))
    def unread_count(self, request: Request):
        queryset = self.get_queryset()
        unread_count = queryset.filter(unread=True).count()
        return Response({'unread_count': unread_count}, status=status.HTTP_200_OK)

    # <Wayne Shih> 13-Mar-2022
    # URL:
    # - POST /api/notifications/mark-all-as-read/
    @action(methods=['POST'], detail=False, url_path='mark-all-as-read')
    @method_decorator(ratelimit(key='user_or_ip', rate='3/s', method='POST', block=True))
    def mark_all_as_read(self, request: Request):
        queryset = self.get_queryset()
        # <Wayne Shih> 13-Mar-2022
        # queryset has its own update() method
        # https://docs.djangoproject.com/en/4.0/ref/models/querysets/#django.db.models.query.QuerySet.update
        num_updated = queryset.filter(unread=True).update(unread=False)
        return Response({'marked_count': num_updated}, status=status.HTTP_200_OK)
