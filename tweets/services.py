# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#   Tweet services provide Tweet helpers for other APIs
#
# =================================================================================================
#    Date      Name                    Description of Change
# 27-Mar-2022  Wayne Shih              Initial create
# 29-May-2022  Wayne Shih              Add uer tweets cache
# $HISTORY$
# =================================================================================================


from django.conf import settings

from tweets.models import Tweet, TweetPhoto
from twitter.caches import USER_TWEETS_PATTERN
from utils.redis_client import RedisClient
from utils.redis_serializers import DjangoModelSerializer


class TweetService(object):

    @classmethod
    def create_tweet_photos(cls, tweet: Tweet, photo_files):
        if not photo_files:
            return

        tweet_photos = []
        for index, photo_file in enumerate(photo_files):
            tweet_photo = TweetPhoto(
                tweet_id=tweet.id,
                user_id=tweet.user_id,
                file=photo_file,
                order=index,
            )
            tweet_photos.append(tweet_photo)

        # <Wayne Shih> 27-Mar-2022
        # Use bulk create instead, then only one insert query
        TweetPhoto.objects.bulk_create(tweet_photos)

    @classmethod
    def _load_tweets_to_cache(cls, key, tweets):
        conn = RedisClient.get_connection()
        serialized_list = [DjangoModelSerializer.serialize(tweet) for tweet in tweets]
        if serialized_list:
            conn.rpush(key, *serialized_list)
            conn.expire(key, settings.REDIS_KEY_EXPIRE_TIME)

    @classmethod
    def _get_tweet_queryset(cls, user_id, view=None):
        if view is not None:
            return view.filter_queryset(
                Tweet.objects.all().order_by('-created_at').prefetch_related('user')
            )
        return Tweet.objects.filter(user_id=user_id)\
            .order_by('-created_at')\
            .prefetch_related('user')

    @classmethod
    def get_cached_tweets(cls, user_id, view=None):
        # <Wayne Shih> 29-May-2022
        # Queryset is in fact lazy loading, so this line doesn't trigger db query yet
        tweets = cls._get_tweet_queryset(user_id, view)
        key = USER_TWEETS_PATTERN.format(user_id=user_id)

        conn = RedisClient.get_connection()
        if conn.exists(key):
            serialized_list = conn.lrange(key, 0, -1)
            return [
                DjangoModelSerializer.deserialize(serialized_data)
                for serialized_data in serialized_list
            ]

        cls._load_tweets_to_cache(key, tweets)
        return list(tweets)

    @classmethod
    def push_tweet_to_user_tweets_cache(cls, tweet):
        # <Wayne Shih> 29-May-2022
        # Queryset is in fact lazy loading, so this line doesn't trigger db query yet
        tweets = Tweet.objects.filter(user_id=tweet.user_id).order_by('-created_at')
        key = USER_TWEETS_PATTERN.format(user_id=tweet.user_id)
        conn = RedisClient.get_connection()
        if conn.exists(key):
            conn.lpush(key, DjangoModelSerializer.serialize(tweet))
            return

        cls._load_tweets_to_cache(key, tweets)
