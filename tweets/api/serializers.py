# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#       - Serializer for tweets api
#
#       - Serializers allow complex data such as querysets and model instances to be converted to
#         native Python datatypes that can then be easily rendered into JSON, XML or other content
#         types.
#       - Can be used as a validator to validate if request is valid
#
#       Ref: https://www.django-rest-framework.org/api-guide/serializers/
#
# =================================================================================================
#    Date      Name                    Description of Change
# 06-Sep-2021  Wayne Shih              Initial create
# 10-Oct-2021  Wayne Shih              React to pylint checks
# 27-Nov-2021  Wayne Shih              Add TweetSerializerWithComments for tweet retrieve api
# 27-Nov-2021  Wayne Shih              Use SerializerMethodField instead to prefetch for comments
# 12-Mar-2022  Wayne Shih              Insert likes to tweet serializers
# 17-Mar-2022  Wayne Shih              Add TweetSerializerForNotifications
# 30-Mar-2022  Wayne Shih              Add tweet photo to serializers
# $HISTORY$
# =================================================================================================


from rest_framework import serializers

from accounts.api.serializers import UserSerializerForTweet
from comments.api.serializers import CommentSerializer
from likes.api.serializers import LikeSerializer
from likes.services import LikeService
from tweets.constants import TWEET_PHOTOS_UPLOAD_LIMIT
from tweets.models import Tweet
from tweets.services import TweetService


class TweetSerializer(serializers.ModelSerializer):
    user = UserSerializerForTweet()
    comments_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    has_liked = serializers.SerializerMethodField()
    photo_urls = serializers.SerializerMethodField()

    class Meta:
        model = Tweet
        fields = (
            'id',
            'user',
            'created_at',
            'content',
            'comments_count',
            'likes_count',
            'has_liked',
            'photo_urls',
        )

    def get_comments_count(self, obj):
        return obj.comment_set.count()

    def get_likes_count(self, obj):
        return obj.like_set.count()

    def get_has_liked(self, obj):
        return LikeService.get_has_liked(self.context['request'].user, obj)

    def get_photo_urls(self, obj):
        photos = obj.tweetphoto_set.filter(has_deleted=False).order_by('order')
        photo_urls = [
            photo.file.url
            for photo in photos
        ]
        return photo_urls

    # <Wayne Shih> 30-Mar-2022
    # TODO:
    #   In this future, could extend the api to group photos by status.
    #   By passing status to get_photo_urls(), and make it do the filter.
    #   Note that need to think if there is a way to prefetch all statuses
    #   to avoid multiple db queries.
    #   Also, to add index ('tweet_id', 'has_deleted', 'status', 'order') on the model might help.
    # def get_pending_photo_urls(self, obj):
    #     return self.get_photo_urls(obj, TweetPhotoStatus.PENDING)
    #
    # def get_approved_photo_urls(self, obj):
    #     return self.get_photo_urls(obj, TweetPhotoStatus.APPROVED)
    #
    # def get_rejected_photo_urls(self, obj):
    #     return self.get_photo_urls(obj, TweetPhotoStatus.REJECTED)


class TweetSerializerForDetail(TweetSerializer):
    # <Wayne Shih> 26-Nov-2021
    # - https://docs.djangoproject.com/en/3.2/topics/db/queries/#following-relationships-backward
    # - https://www.django-rest-framework.org/api-guide/fields/#using-source
    # It seems like source='comment_set' is not able to prefetch_related for comments
    # comments = CommentSerializer(source='comment_set', many=True)
    #
    # <Wayne Shih> 27-Nov-2021
    # Use SerializerMethodField instead in order to prefetch_related for comments
    comments = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()

    class Meta:
        model = Tweet
        fields = (
            'id',
            'user',
            'created_at',
            'content',
            'comments',
            'comments_count',
            'likes',
            'likes_count',
            'has_liked',
            'photo_urls',
        )

    def get_comments(self, obj):
        return CommentSerializer(
            obj.comment_set.all().prefetch_related('user'),
            many=True,
            context={'request': self.context['request']},
        ).data

    def get_likes(self, obj):
        return LikeSerializer(
            obj.like_set.all().prefetch_related('user'),
            many=True,
        ).data


class TweetSerializerForCreate(serializers.ModelSerializer):
    content = serializers.CharField(min_length=6, max_length=255)
    # <Wayne Shih> 26-Mar-2022
    # https://www.django-rest-framework.org/api-guide/fields/#listfield
    # https://www.django-rest-framework.org/api-guide/fields/#filefield
    photo_files = serializers.ListField(
        child=serializers.FileField(),
        allow_empty=True,
        max_length=TWEET_PHOTOS_UPLOAD_LIMIT,
        required=False,
        style={'template': 'upload_multiple_files.html'},
    )

    class Meta:
        model = Tweet
        fields = ('content', 'photo_files')

    def validate(self, attrs):
        photos = attrs.setdefault('photo_files', [])
        if len(photos) > TWEET_PHOTOS_UPLOAD_LIMIT:
            raise serializers.ValidationError({
                'photo_files': f'No more than {TWEET_PHOTOS_UPLOAD_LIMIT} photos for a tweet'
            })
        return attrs

    # <Wayne Shih> 06-Sep-2021
    # - https://www.django-rest-framework.org/api-guide/serializers/#saving-instances
    def create(self, validated_data):
        user_id = self.context['request'].user.id
        content = validated_data['content']
        tweet = Tweet.objects.create(user_id=user_id, content=content)
        TweetService.create_tweet_photos(tweet, validated_data.get('photo_files'))
        return tweet


class TweetSerializerForNotifications(serializers.ModelSerializer):

    class Meta:
        model = Tweet
        fields = (
            'id',
            'content',
            'created_at',
        )
