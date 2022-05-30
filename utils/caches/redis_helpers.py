# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#   utils provide user with Redis helpers for other APIs
#
# =================================================================================================
#    Date      Name                    Description of Change
# 30-May-2022  Wayne Shih              Initial create
# 30-May-2022  Wayne Shih              Refactor utils file structure
# $HISTORY$
# =================================================================================================


from django.conf import settings

from utils.caches.redis_client import RedisClient
from utils.caches.redis_serializers import DjangoModelSerializer


class RedisHelper(object):

    @classmethod
    def _load_objects_to_cache(cls, key, queryset):
        conn = RedisClient.get_connection()
        serialized_list = [DjangoModelSerializer.serialize(obj) for obj in queryset]
        if serialized_list:
            conn.rpush(key, *serialized_list)
            conn.expire(key, settings.REDIS_KEY_EXPIRE_TIME)

    @classmethod
    def load_objects(cls, key, queryset):
        conn = RedisClient.get_connection()
        if conn.exists(key):
            serialized_list = conn.lrange(key, 0, -1)
            return [
                DjangoModelSerializer.deserialize(serialized_data)
                for serialized_data in serialized_list
            ]

        cls._load_objects_to_cache(key, queryset)
        return list(queryset)

    @classmethod
    def push_objects(cls, key, obj, queryset):
        conn = RedisClient.get_connection()
        if conn.exists(key):
            conn.lpush(key, DjangoModelSerializer.serialize(obj))
            return

        cls._load_objects_to_cache(key, queryset)
