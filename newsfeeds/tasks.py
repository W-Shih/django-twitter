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
# $HISTORY$
# =================================================================================================


from celery import shared_task

from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed
from utils.time_constants import ONE_HOUR


@shared_task(time_limit=ONE_HOUR)
def fanout_newsfeeds_task(tweet_id, tweet_user_id):
    from newsfeeds.services import NewsFeedService

    follower_ids = FriendshipService.get_follower_ids(tweet_user_id)
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
