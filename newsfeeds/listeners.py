# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#       receivers of signal-listener mechanisms for newsfeed models
#
# =================================================================================================
#    Date      Name                    Description of Change
# 30-May-2022  Wayne Shih              Initial create
# $HISTORY$
# =================================================================================================


# <Wayne Shih> 29-May-2022
# https://docs.djangoproject.com/en/3.1/topics/signals/#receiver-functions
def push_newsfeed_to_cache(sender, instance, created, **kwargs):
    if not created:
        return

    from newsfeeds.services import NewsFeedService
    NewsFeedService.push_newsfeed_to_cache(instance)
