# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#       receivers of signal-listener mechanisms for tweet models
#
# =================================================================================================
#    Date      Name                    Description of Change
# 29-May-2022  Wayne Shih              Initial create
# $HISTORY$
# =================================================================================================


# <Wayne Shih> 29-May-2022
# https://docs.djangoproject.com/en/3.1/topics/signals/#receiver-functions
def push_tweet_to_user_tweets_cache(sender, instance, created, **kwargs):
    if not created:
        return

    from tweets.services import TweetService
    TweetService.push_tweet_to_user_tweets_cache(instance)
