# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#       receivers of signal-listener mechanisms for friendship model
#
# =================================================================================================
#    Date      Name                    Description of Change
# 30-Apr-2022  Wayne Shih              Initial create
# $HISTORY$
# =================================================================================================


# <Wayne Shih> 30-Apr-2022
# https://docs.djangoproject.com/en/3.1/topics/signals/#receiver-functions
def invalidate_followings_cache(sender, instance, **kwargs):
    from friendships.services import FriendshipService
    FriendshipService.invalidate_followings_cache(instance.from_user_id)
