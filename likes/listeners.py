# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#       receivers of signal-listener mechanisms for like models
#
# =================================================================================================
#    Date      Name                    Description of Change
# 05-Jun-2022  Wayne Shih              Initial create
# 09-Jun-2022  Wayne Shih              Cache reacts to likes_count change
# $HISTORY$
# =================================================================================================


from utils.caches.redis_helpers import RedisHelper


# <Wayne Shih> 05-Jun-2022
# https://docs.djangoproject.com/en/3.1/topics/signals/#receiver-functions
def increase_likes_count(sender, instance, created, **kwargs):
    from django.db.models import F
    from tweets.models import Tweet

    if not created:
        return

    model_class = instance.content_type.model_class()
    # <Wayne Shih> 05-Jun-2022
    # TODO: remove this check after adding comment model denormalization for likes_count
    if model_class != Tweet:
        return

    # <Wayne Shih> 05-Jun-2022
    # https://docs.djangoproject.com/en/4.0/ref/models/expressions/#f-expressions
    model_class.objects.filter(id=instance.object_id).update(likes_count=F('likes_count') + 1)
    RedisHelper.incr_count(instance.content_object, 'likes_count')


def decrease_likes_count(sender, instance, **kwargs):
    from django.db.models import F
    from tweets.models import Tweet

    model_class = instance.content_type.model_class()
    # <Wayne Shih> 05-Jun-2022
    # TODO: remove this check after adding comment model denormalization for likes_count
    if model_class != Tweet:
        return

    # <Wayne Shih> 05-Jun-2022
    # https://docs.djangoproject.com/en/4.0/ref/models/expressions/#f-expressions
    model_class.objects.filter(id=instance.object_id).update(likes_count=F('likes_count') - 1)
    RedisHelper.decr_count(instance.content_object, 'likes_count')
