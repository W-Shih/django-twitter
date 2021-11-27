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
# $HISTORY$
# =================================================================================================


from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from newsfeeds.services import NewsFeedService
from tweets.api.serializers import (
    TweetSerializer,
    TweetSerializerForCreate,
    TweetSerializerWithComments,
)
from tweets.models import Tweet


class TweetViewSet(viewsets.GenericViewSet):
    # <Wayne Shih> 06-Sep-2021
    # rest_framework will use serializer_class to be the POST format at the rest page
    # - https://www.django-rest-framework.org/api-guide/generic-views/#genericapiview
    serializer_class = TweetSerializerForCreate
    # <Wayne Shih> 27-Nov-2021
    # TODO:
    #   prefetch_related for comments
    queryset = Tweet.objects.all()

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
        return Response(TweetSerializerWithComments(tweet).data, status=status.HTTP_200_OK)

    # <Wayne Shih> 06-Sep-2021
    # URL:
    # - GET /api/tweets/?user_id=1 --> OK
    # - GET /api/tweets/ --> Not OK
    # - https://www.django-rest-framework.org/api-guide/viewsets/#viewset-actions
    # - https://www.django-rest-framework.org/api-guide/viewsets/#genericviewset
    # - https://www.django-rest-framework.org/api-guide/viewsets/#example
    def list(self, request: Request):
        if 'user_id' not in request.query_params:
            return Response({'message': 'Missing user_id.'}, status=status.HTTP_400_BAD_REQUEST)

        # <Wayne Shih> 06-Sep-2021
        # Does it need to check if user_id exist? -- Keep silence for now
        user_id = request.query_params['user_id']
        tweets = Tweet.objects.filter(user_id=user_id)
        # print('--- sql --- \n{}'.format(tweets.query))
        return Response({
            'tweets': TweetSerializer(tweets, many=True).data,
        }, status=status.HTTP_200_OK)

    # <Wayne Shih> 06-Sep-2021
    # URL:
    # - POST /api/tweets/
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
        return Response(TweetSerializer(tweet).data, status=status.HTTP_201_CREATED)
