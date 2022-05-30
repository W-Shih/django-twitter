# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#   Tweet services provide Tweet helpers for other APIs
#
# =================================================================================================
#    Date      Name                    Description of Change
# 27-Mar-2022  Wayne Shih              Initial create
# 29-May-2022  Wayne Shih              Add uer tweets cache, react to redis helper
# $HISTORY$
# =================================================================================================


from tweets.models import Tweet, TweetPhoto
from twitter.caches import USER_TWEETS_PATTERN
from utils.caches.redis_helpers import RedisHelper


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
        return RedisHelper.load_objects(key, tweets)

    @classmethod
    def push_tweet_to_user_tweets_cache(cls, tweet):
        # <Wayne Shih> 29-May-2022
        # Queryset is in fact lazy loading, so this line doesn't trigger db query yet
        tweets = Tweet.objects.filter(user_id=tweet.user_id).order_by('-created_at')
        key = USER_TWEETS_PATTERN.format(user_id=tweet.user_id)
        RedisHelper.push_objects(key, tweet, tweets)
