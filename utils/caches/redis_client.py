# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#   utils provide with redis wraps for other APIs
#
# =================================================================================================
#    Date      Name                    Description of Change
# 28-May-2022  Wayne Shih              Initial create
# 30-May-2022  Wayne Shih              Refactor utils file structure
# $HISTORY$
# =================================================================================================


import redis

from django.conf import settings


class RedisClient:
    conn = None

    @classmethod
    def get_connection(cls):
        if cls.conn:
            return cls.conn

        # <Wayne Shih> 28-May-2022
        # https://github.com/redis/redis-py#getting-started
        cls.conn = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
        )
        return cls.conn

    @classmethod
    def clear(cls):
        if not settings.TESTING:
            raise Exception('You can NOT flush redis other than in testing environment')

        # <Wayne Shih> 28-May-2022
        # https://redis.io/commands/?name=flush
        # https://stackoverflow.com/questions/45916183/how-do-i-to-flush-redis-db-from-python-redis
        conn = cls.get_connection()
        conn.flushdb()
