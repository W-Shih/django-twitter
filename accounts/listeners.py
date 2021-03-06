# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#       receivers of signal-listener mechanisms for user and user profile models
#
# =================================================================================================
#    Date      Name                    Description of Change
# 25-May-2022  Wayne Shih              Initial create
# 27-May-2022  Wayne Shih              React to memcached helper
# $HISTORY$
# =================================================================================================


# <Wayne Shih> 25-May-2022
# https://docs.djangoproject.com/en/3.1/topics/signals/#receiver-functions
def invalidate_profile_cache(sender, instance, **kwargs):
    from accounts.services import UserService
    UserService.invalidate_profile_cache(instance.user_id)
