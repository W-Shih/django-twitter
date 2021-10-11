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
# 08-Sep-2021  Wayne Shih              Initial create
# 10-Oct-2021  Wayne Shih              React to pylint checks
# $HISTORY$
# =================================================================================================


from django.contrib.auth.models import User
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from friendships.api.serializers import (
    FollowerSerializer,
    FollowingSerializer,
    FriendshipSerializerForCreate,
)
from friendships.models import Friendship


class FriendshipViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = FriendshipSerializerForCreate

    def list(self, reqeust):
        return Response({
            'message': {
                'Get followers': {
                    'method': 'GET',
                    'url': '/api/friendships/{to_user_id_pk}/followers/',
                },
                'Get followings': {
                    'method': 'GET',
                    'url': '/api/friendships/{from_user_id_pk}/followings/',
                },
                'Follow someone': {
                    'method': 'POST',
                    'url': 'api/friendships/{to_user_id_pk}/follow/',
                },
                'Unfollow someone': {
                    'method': 'POST',
                    'url': '/api/friendships/{to_user_id_pk}/unfollow/',
                },
            }
        }, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followers(self, request, pk):
        to_user = self.get_object()
        followers = Friendship.objects.filter(to_user_id=to_user.id).order_by('-created_at')
        # print(followers[0].from_user)
        return Response({
            'followers': FollowerSerializer(followers, many=True).data,
        }, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followings(self, request, pk):
        from_user = self.get_object()
        followings = Friendship.objects.filter(from_user_id=from_user.id).order_by('-created_at')
        # print(followings[0].from_user)
        return Response({
            'followings': FollowingSerializer(followings, many=True).data,
        }, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def follow(self, request: Request, pk):
        to_user = self.get_object()
        from_user = request.user

        if Friendship.objects.filter(
            from_user_id=from_user.id,
            to_user_id=to_user.id,
        ).exists():
            return Response({
                'success': True,
                'duplicate': True,
            }, status=status.HTTP_201_CREATED)

        serializer = FriendshipSerializerForCreate(data={
            'from_user_id': from_user.id,
            'to_user_id': to_user.id,
        })
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check input.',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        friendship = serializer.save()
        return Response({
            'success': True,
            'following': FollowingSerializer(friendship).data,
        }, status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def unfollow(self, request: Request, pk):
        to_user = self.get_object()
        from_user = request.user

        if from_user.id == to_user.id:
            return Response({
                'success': False,
                'message': 'You cannot unfollow yourself.',
            }, status=status.HTTP_400_BAD_REQUEST)

        if not Friendship.objects.filter(
            from_user_id=from_user.id,
            to_user_id=to_user.id,
        ).exists():
            return Response({
                'success': True,
                'num_deleted': 0,
            }, status=status.HTTP_200_OK)

        num_deleted, _ = Friendship.objects.filter(
            from_user_id=from_user.id,
            to_user_id=to_user.id,
        ).delete()
        return Response({
            'success': True,
            'num_deleted': num_deleted,
        }, status=status.HTTP_200_OK)
