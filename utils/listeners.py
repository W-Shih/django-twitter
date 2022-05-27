# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#       receivers of signal-listener mechanisms for models
#
# =================================================================================================
#    Date      Name                    Description of Change
# 27-May-2022  Wayne Shih              Initial create
# $HISTORY$
# =================================================================================================


# <Wayne Shih> 26-May-2022
# https://docs.djangoproject.com/en/3.1/topics/signals/#receiver-functions
def invalidate_object_cache(sender, instance, **kwargs):
    from utils.memcached_helpers import MemcachedHelper
    MemcachedHelper.invalidate_object_cache(instance.__class__, instance.id)
