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
# 05-Jun-2022  Wayne Shih              Only cache REDIS_LIST_SIZE_LIMIT in redis
# 09-Jun-2022  Wayne Shih              Add helpers to cache and get counts
# $HISTORY$
# =================================================================================================


from django.conf import settings

from utils.caches.redis_client import RedisClient
from utils.caches.redis_serializers import DjangoModelSerializer


class RedisHelper(object):

    @classmethod
    def _load_objects_to_cache(cls, key, queryset):
        conn = RedisClient.get_connection()
        serialized_list = [
            DjangoModelSerializer.serialize(obj)
            for obj in queryset[:settings.REDIS_LIST_SIZE_LIMIT]
        ]
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
            conn.ltrim(key, 0, settings.REDIS_LIST_SIZE_LIMIT - 1)
            return

        cls._load_objects_to_cache(key, queryset)

    @classmethod
    def _get_key_for_count(cls, obj, attr):
        return f'{obj.__class__.__name__}:{obj.id}:{attr}'

    @classmethod
    def _refill_count_cache_from_db(cls, key, obj, attr):
        conn = RedisClient.get_connection()
        obj.refresh_from_db()
        conn.set(key, getattr(obj, attr))
        conn.expire(key, settings.REDIS_KEY_EXPIRE_TIME)
        return getattr(obj, attr)

    @classmethod
    def get_count(cls, obj, attr):
        conn = RedisClient.get_connection()
        key = cls._get_key_for_count(obj, attr)
        if conn.exists(key):
            return int(conn.get(key))

        return cls._refill_count_cache_from_db(key, obj, attr)

    @classmethod
    def incr_count(cls, obj, attr):
        conn = RedisClient.get_connection()
        key = cls._get_key_for_count(obj, attr)
        if conn.exists(key):
            return conn.incr(key)

        # <Wayne Shih> 05-Jun-2022
        # Caller needs to guarantee that it updates the count in db itself.
        # This helper is only responsible for the count in redis cache.
        return cls._refill_count_cache_from_db(key, obj, attr)

    @classmethod
    def decr_count(cls, obj, attr):
        conn = RedisClient.get_connection()
        key = cls._get_key_for_count(obj, attr)
        if conn.exists(key):
            return conn.decr(key)

        # <Wayne Shih> 05-Jun-2022
        # Caller needs to guarantee that it updates the count in db itself.
        # This helper is only responsible for the count in redis cache.
        return cls._refill_count_cache_from_db(key, obj, attr)
