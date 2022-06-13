# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#   NewsFeed services provide NewsFeed helpers for other APIs
#
# =================================================================================================
#    Date      Name                    Description of Change
# 18-Oct-2021  Wayne Shih              Initial create
# 30-May-2022  Wayne Shih              Add uer newsfeeds cache, react to redis helper
# 12-Jun-2022  Wayne Shih              Use message queue to fanout newsfeeds
# 12-Jun-2022  Wayne Shih              Make fanout robust
# $HISTORY$
# =================================================================================================


from newsfeeds.models import NewsFeed
from newsfeeds.tasks import fanout_newsfeeds_main_task
from tweets.models import Tweet
from twitter.caches import USER_NEWSFEEDS_PATTERN
from utils.caches.redis_helpers import RedisHelper


class NewsFeedService(object):

    @classmethod
    def fanout_to_followers(cls, tweet: Tweet):
        # <Wayne Shih> 11-Jun-2022
        # User should be able to see own tweet as soon as possible
        NewsFeed.objects.create(user_id=tweet.user_id, tweet_id=tweet.id)
        fanout_newsfeeds_main_task.delay(tweet.id, tweet.user_id)

    @classmethod
    def get_cached_newsfeeds(cls, user_id):
        # <Wayne Shih> 30-May-2022
        # Queryset is in fact lazy loading, so this line doesn't trigger db query yet
        newsfeeds = NewsFeed.objects.filter(user_id=user_id).order_by('-created_at')
        key = USER_NEWSFEEDS_PATTERN.format(user_id=user_id)
        return RedisHelper.load_objects(key, newsfeeds)

    @classmethod
    def push_newsfeed_to_cache(cls, newsfeed):
        # <Wayne Shih> 30-May-2022
        # Queryset is in fact lazy loading, so this line doesn't trigger db query yet
        newsfeeds = NewsFeed.objects.filter(user_id=newsfeed.user_id).order_by('-created_at')
        key = USER_NEWSFEEDS_PATTERN.format(user_id=newsfeed.user_id)
        RedisHelper.push_objects(key, newsfeed, newsfeeds)
