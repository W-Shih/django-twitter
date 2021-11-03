# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#   NewsFeed services provide NewsFeed helpers for other APIs
#
# =================================================================================================
#    Date      Name                    Description of Change
# 18-Oct-2021  Wayne Shih              Initial create
# $HISTORY$
# =================================================================================================


from tweets.models import Tweet
from newsfeeds.models import NewsFeed
from friendships.services import FriendshipService


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
