# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#   Define async tasks for workers to execute
#     - https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html
#     - https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html#using-the-shared-task-decorator
#
# =================================================================================================
#    Date      Name                    Description of Change
# 12-Jun-2022  Wayne Shih              Initial create
# 12-Jun-2022  Wayne Shih              Make fanout robust
# 14-Jun-2022  Wayne Shih              Fix fanout log
# $HISTORY$
# =================================================================================================


import math

from celery import shared_task

from friendships.services import FriendshipService
from newsfeeds.constants import FANOUT_BATCH_SIZE
from newsfeeds.models import NewsFeed
from utils.time_constants import ONE_HOUR


@shared_task(routing_key='default', time_limit=ONE_HOUR)
def fanout_newsfeeds_main_task(tweet_id, tweet_user_id):
    follower_ids = FriendshipService.get_follower_ids(tweet_user_id)
    batch_from, batch_end = 0, FANOUT_BATCH_SIZE
    while len(follower_ids[batch_from:batch_end]) > 0:
        fanout_newsfeeds_batch_task.delay(tweet_id, follower_ids[batch_from:batch_end])
        batch_from, batch_end = batch_end, batch_end + FANOUT_BATCH_SIZE

    return f'{math.ceil(len(follower_ids) / FANOUT_BATCH_SIZE)} batches created, '\
           f'going to fanout {len(follower_ids)} newsfeeds.'


@shared_task(routing_key='newsfeeds', time_limit=ONE_HOUR)
def fanout_newsfeeds_batch_task(tweet_id, follower_ids):
    from newsfeeds.services import NewsFeedService

    # follower_ids = FriendshipService.get_follower_ids(tweet_user_id)
    newsfeeds = [
        NewsFeed(user_id=follower_id, tweet_id=tweet_id)
        for follower_id in follower_ids
    ]
    # <Wayne Shih> 18-Oct-2021
    # Use bulk create instead, then only one insert query
    NewsFeed.objects.bulk_create(newsfeeds)

    # <Wayne Shih> 30-May-2022
    # Note that bulk_create() will NOT trigger post_save() signal,
    # so here needs to push newsfeeds to cache on our own.
    for newsfeed in newsfeeds:
        NewsFeedService.push_newsfeed_to_cache(newsfeed)

    return f'{len(newsfeeds)} newsfeeds created.'
