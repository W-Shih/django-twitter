# =================================================================================================
# File description:
#           Newsfeed model unit tests
#
# =================================================================================================
#    Date      Name                    Description of Change
# 17-Oct-2021  Wayne Shih              Initial create
# 05-Nov-2021  Wayne Shih              Fix typo
# 26-May-2022  Wayne Shih              Add clear cache before each test
# 30-May-2022  Wayne Shih              Test user newsfeeds cache, react to utils file structure refactor
# 12-Jun-2022  Wayne Shih              Add tests for fanout_newsfeeds_main_task()
# $HISTORY$
# =================================================================================================


import re

from newsfeeds.constants import FANOUT_BATCH_SIZE
from newsfeeds.models import NewsFeed
from newsfeeds.services import NewsFeedService
from newsfeeds.tasks import fanout_newsfeeds_main_task
from testing.testcases import TestCase
from twitter.caches import USER_NEWSFEEDS_PATTERN
from utils.caches.redis_client import RedisClient


class NewsfeedTests(TestCase):

    def setUp(self):
        self.clear_cache()
        self.user = self.create_user(username='cavs_lbj23')
        self.tweet = self.create_tweet(user=self.user, content='This is for u!')
        self.newsfeed = NewsFeed.objects.create(
            user=self.user,
            tweet=self.tweet
        )

    def test_newsfeed_model_attributes(self):
        self.assertEqual(hasattr(NewsFeed, 'id'), True)
        self.assertEqual(hasattr(NewsFeed, 'user'), True)
        self.assertEqual(hasattr(NewsFeed, 'user_id'), True)
        self.assertEqual(hasattr(NewsFeed, 'tweet'), True)
        self.assertEqual(hasattr(NewsFeed, 'tweet_id'), True)
        self.assertEqual(hasattr(NewsFeed, 'created_at'), True)
        self.assertEqual(hasattr(self.user, 'newsfeed_set'), True)
        self.assertEqual(hasattr(self.tweet, 'newsfeed_set'), True)

    def test_newsfeed_meta(self):
        self.assertEqual(len(NewsFeed._meta.index_together), 1)
        self.assertEqual(len(NewsFeed._meta.unique_together), 1)
        self.assertEqual(len(NewsFeed._meta.ordering), 2)

        self.assertEqual(
            bool(re.search('user(.*?)created_at', str(NewsFeed._meta.index_together))),
            True
        )

        self.assertEqual(
            bool(re.search('user(.*?)tweet', str(NewsFeed._meta.unique_together))),
            True
        )

        self.assertEqual(NewsFeed._meta.ordering, ('user', '-created_at',))

    def test_newsfeed_on_delete(self):
        self.user.delete()
        self.assertEqual(NewsFeed.objects.first().user, None)
        self.tweet.delete()
        self.assertEqual(NewsFeed.objects.first().tweet, None)

    def test_time(self):
        old_created_time = self.newsfeed.created_at
        self.newsfeed.tweet = None
        self.newsfeed.save()
        self.assertEqual(old_created_time, self.newsfeed.created_at)

    def test_newsfeed_str(self):
        self.assertEqual(
            str(self.newsfeed.created_at) in str(self.newsfeed),
            True
        )
        self.assertEqual(
            str(self.newsfeed.user_id) in str(self.newsfeed),
            True
        )
        self.assertEqual(
            str(self.newsfeed.tweet_id) in str(self.newsfeed),
            True
        )

        message = '-- {created_at} inbox of {user}: {tweet} --'
        self.assertEqual(message.format(
            created_at=self.newsfeed.created_at,
            user=self.newsfeed.user,
            tweet=self.newsfeed.tweet,
        ), str(self.newsfeed))


class NewsfeedCacheTests(TestCase):

    def setUp(self):
        self.clear_cache()
        self.kd35 = self.create_user(username='kd35')

    def test_get_user_newsfeeds(self):
        newsfeed_ids = []
        for i in range(3):
            tweet = self.create_tweet(self.kd35, f'kd newsfeed - {i}')
            newsfeed = self.create_newsfeed(self.kd35, tweet)
            newsfeed_ids.append(newsfeed.id)
        newsfeed_ids = newsfeed_ids[::-1]

        # test cache miss  <Wayne Shih> 30-May-2022
        conn = RedisClient.get_connection()
        RedisClient.clear()
        key_kd35 = USER_NEWSFEEDS_PATTERN.format(user_id=self.kd35.id)
        self.assertEqual(conn.exists(key_kd35), False)

        kd35_newsfeeds = NewsFeedService.get_cached_newsfeeds(self.kd35.id)
        self.assertEqual(type(kd35_newsfeeds), list)
        self.assertEqual([feed.id for feed in kd35_newsfeeds], newsfeed_ids)
        self.assertEqual(conn.exists(key_kd35), True)

        # test cache hit  <Wayne Shih> 30-May-2022
        self.assertEqual(conn.exists(key_kd35), True)
        kd35_newsfeeds = NewsFeedService.get_cached_newsfeeds(self.kd35.id)
        self.assertEqual(conn.exists(key_kd35), True)
        self.assertEqual(type(kd35_newsfeeds), list)
        self.assertEqual([feed.id for feed in kd35_newsfeeds], newsfeed_ids)

        # test push newsfeed to cache while key exists  <Wayne Shih> 30-May-2022
        self.assertEqual(conn.exists(key_kd35), True)
        new_tweet = self.create_tweet(self.kd35, 'I am going to join GW - new')
        new_kd35_feed = self.create_newsfeed(self.kd35, new_tweet)
        newsfeed_ids.insert(0, new_kd35_feed.id)
        self.assertEqual(conn.exists(key_kd35), True)

        kd35_newsfeeds = NewsFeedService.get_cached_newsfeeds(self.kd35.id)
        self.assertEqual(type(kd35_newsfeeds), list)
        self.assertEqual([feed.id for feed in kd35_newsfeeds], newsfeed_ids)

        # test push newsfeed to cache while key does NOT exist  <Wayne Shih> 30-May-2022
        RedisClient.clear()
        self.assertEqual(conn.exists(key_kd35), False)
        new_tweet = self.create_tweet(self.kd35, 'I am going to join Nets - new')
        new_kd35_feed = self.create_newsfeed(self.kd35, new_tweet)
        newsfeed_ids.insert(0, new_kd35_feed.id)
        self.assertEqual(conn.exists(key_kd35), True)

        kd35_newsfeeds = NewsFeedService.get_cached_newsfeeds(self.kd35.id)
        self.assertEqual([feed.id for feed in kd35_newsfeeds], newsfeed_ids)
        self.assertEqual(type(kd35_newsfeeds), list)


class NewsfeedTaskTests(TestCase):

    def setUp(self):
        self.clear_cache()

        self.lbj23, self.lbj23_client = self.create_user_and_auth_client(username='lbj23')
        self.kd35, self.kd35_client = self.create_user_and_auth_client(username='kd35')
        self.create_friendship(self.kd35, self.lbj23)

    def test_fanout_main_task(self):
        expected_msg = '{num_batches} batches created, going to fanout {num_newsfeeds} newsfeeds.'
        cached_kd35_feeds = NewsFeedService.get_cached_newsfeeds(self.kd35.id)
        self.assertEqual(len(cached_kd35_feeds), 0)
        self.assertEqual(NewsFeed.objects.count(), 0)

        self.lbj23_tweet1 = self.create_tweet(self.lbj23, 'I am coming home!!')
        msg = fanout_newsfeeds_main_task(self.lbj23_tweet1.id, self.lbj23.id)
        cached_kd35_feeds = NewsFeedService.get_cached_newsfeeds(self.kd35.id)
        self.assertEqual(len(cached_kd35_feeds), 1)
        # <Wayne Shih> 12-Jun-2022
        # Note that fanout_newsfeeds_main_task() is not responsible for fanouting the newsfeed to
        # the twitter user itself. fanout_newsfeeds_main_task() only fanouts the newsfeed to the
        # user's followers.
        self.assertEqual(NewsFeed.objects.count(), 1)
        self.assertEqual(msg, expected_msg.format(num_batches=1, num_newsfeeds=1))

        for i in range(FANOUT_BATCH_SIZE):
            user = self.create_user(f'user:{i}')
            self.create_friendship(user, self.lbj23)
        self.lbj23_tweet2 = self.create_tweet(self.lbj23, 'This is for u!!')
        msg = fanout_newsfeeds_main_task(self.lbj23_tweet2.id, self.lbj23.id)
        cached_kd35_feeds = NewsFeedService.get_cached_newsfeeds(self.kd35.id)
        self.assertEqual(len(cached_kd35_feeds), 2)
        self.assertEqual(NewsFeed.objects.count(), 1 + (1 + FANOUT_BATCH_SIZE))
        self.assertEqual(msg, expected_msg.format(
            num_batches=2,
            num_newsfeeds=1 + FANOUT_BATCH_SIZE,
        ))
