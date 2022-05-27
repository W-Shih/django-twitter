# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#   utils provide User Memcached helpers for other APIs
#
# =================================================================================================
#    Date      Name                    Description of Change
# 27-May-2022  Wayne Shih              Initial create
# $HISTORY$
# =================================================================================================


from django.conf import settings
from django.core.cache import caches


cache = caches['default'] if not settings.TESTING else caches['testing']


class MemcachedHelper(object):

    @classmethod
    def get_key(cls, model_class, object_id):
        key = f'{model_class.__name__.lower()}:{object_id}'
        return key

    @classmethod
    def get_object_through_cache(cls, model_class, object_id):
        key = cls.get_key(model_class, object_id)
        obj = cache.get(key)
        if obj is not None:
            return obj

        # <Wayne Shih> 25-May-2022
        # Here expects the user exists in DB, if not, let it throw an error
        # - https://docs.djangoproject.com/en/4.0/ref/models/querysets/#get
        obj = model_class.objects.get(id=object_id)
        cache.set(key, obj)
        return obj

    @classmethod
    def invalidate_object_cache(cls, model_class, object_id):
        key = cls.get_key(model_class, object_id)
        cache.delete(key)
