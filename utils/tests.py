# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#           utils model unit tests
#
# =================================================================================================
#    Date      Name                    Description of Change
# 28-May-2022  Wayne Shih              Initial create
# $HISTORY$
# =================================================================================================


from django.conf import settings

from testing.testcases import TestCase
from utils.redis_client import RedisClient


class UtilsTest(TestCase):

    def setUp(self):
        self.clear_cache()

    def test_redis_client(self):
        conn = RedisClient.get_connection()
        key = 'testing:redis:key'
        conn.lpush(key, 1)
        conn.lpush(key, 2)
        cached_list = conn.lrange(key, 0, -1)
        self.assertEqual(cached_list, [b'2', b'1'])

        RedisClient.clear()
        cached_list = conn.lrange(key, 0, -1)
        self.assertEqual(cached_list, [])

        if settings.TESTING:
            settings.TESTING = False
            error_message = 'You can NOT flush redis other than in testing environment'
            try:
                RedisClient.clear()
            except Exception as error:
                self.assertEqual(error.__str__(), error_message)
            settings.TESTING = True
