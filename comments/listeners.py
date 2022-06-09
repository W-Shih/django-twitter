# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#       receivers of signal-listener mechanisms for comment models
#
# =================================================================================================
#    Date      Name                    Description of Change
# 05-Jun-2022  Wayne Shih              Initial create
# 09-Jun-2022  Wayne Shih              Cache reacts to comments_count change
# $HISTORY$
# =================================================================================================


from utils.caches.redis_helpers import RedisHelper


# <Wayne Shih> 05-Jun-2022
# https://docs.djangoproject.com/en/3.1/topics/signals/#receiver-functions
def increase_comments_count(sender, instance, created, **kwargs):
    from django.db.models import F
    from tweets.models import Tweet

    if not created:
        return

    # <Wayne Shih> 05-Jun-2022
    # https://docs.djangoproject.com/en/4.0/ref/models/expressions/#f-expressions
    Tweet.objects.filter(id=instance.tweet_id).update(comments_count=F('comments_count') + 1)
    RedisHelper.incr_count(instance.tweet, 'comments_count')


def decrease_comments_count(sender, instance, **kwargs):
    from django.db.models import F
    from tweets.models import Tweet

    # <Wayne Shih> 05-Jun-2022
    # https://docs.djangoproject.com/en/4.0/ref/models/expressions/#f-expressions
    Tweet.objects.filter(id=instance.tweet_id).update(comments_count=F('comments_count') - 1)
    RedisHelper.decr_count(instance.tweet, 'comments_count')
