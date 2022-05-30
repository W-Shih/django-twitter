# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#   NewsFeed services provide NewsFeed helpers for other APIs
#
# =================================================================================================
#    Date      Name                    Description of Change
# 18-Oct-2021  Wayne Shih              Initial create
# 30-May-2022  Wayne Shih              Add uer newsfeeds cache, refactor redis helper
# $HISTORY$
# =================================================================================================


from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed
from tweets.models import Tweet
from twitter.caches import USER_NEWSFEEDS_PATTERN
from utils.redis_helpers import RedisHelper


class NewsFeedService(object):

    @classmethod
    def fanout_to_followers(cls, tweet: Tweet):
        to_user_id = tweet.user_id
        follower_ids = FriendshipService.get_follower_ids(to_user_id)
        # <Wayne Shih> 18-Oct-2021
        # User should be able to see own tweet
        follower_ids.append(to_user_id)
        newsfeeds = [
            NewsFeed(user_id=follower_id, tweet_id=tweet.id)
            for follower_id in follower_ids
        ]

        # <Wayne Shih> 18-Oct-2021
        # Use bulk create instead, then only one insert query
        NewsFeed.objects.bulk_create(newsfeeds)

        # <Wayne Shih> 30-May-2022
        # Note that bulk_create() will NOT trigger post_save() signal,
        # so here needs to push newsfeeds to cache on our own.
        for newsfeed in newsfeeds:
            cls.push_newsfeed_to_cache(newsfeed)

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
