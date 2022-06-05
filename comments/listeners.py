# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#       receivers of signal-listener mechanisms for comment models
#
# =================================================================================================
#    Date      Name                    Description of Change
# 05-Jun-2022  Wayne Shih              Initial create
# $HISTORY$
# =================================================================================================


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


def decrease_comments_count(sender, instance, **kwargs):
    from django.db.models import F
    from tweets.models import Tweet

    # <Wayne Shih> 05-Jun-2022
    # https://docs.djangoproject.com/en/4.0/ref/models/expressions/#f-expressions
    Tweet.objects.filter(id=instance.tweet_id).update(comments_count=F('comments_count') - 1)
