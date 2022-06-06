# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#     This is a script to refill likes_count and comments_count in db for model denormalization
#
# =================================================================================================
#    Date      Name                    Description of Change
# 05-Jun-2022  Wayne Shih              Initial create
# $HISTORY$
# =================================================================================================


from django.db.models import F

from tweets.models import Tweet


def refill_counts_in_db_for_tweets(id_start, id_end):
    for tweet_id in range(id_start, id_end):
        tweet_qs = Tweet.objects.filter(id=tweet_id)
        tweet = tweet_qs.first()
        if tweet is None:
            continue
        tweet_qs.update(
            comments_count=tweet.comment_set.count() + (F('comments_count') - F('comments_count')),
            likes_count=tweet.like_set.count() + (F('likes_count') - F('likes_count')),
        )
