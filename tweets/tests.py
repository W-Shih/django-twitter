# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#           tweet model unit tests
#
# =================================================================================================
#    Date      Name                    Description of Change
# 05-Sep-2021  Wayne Shih              Initial create
# 07-Sep-2021  Wayne Shih              React to refactoring TestCase
# 10-Oct-2021  Wayne Shih              React to pylint checks
# 24-Feb-2022  Wayne Shih              Add tests for likes model
# 25-Mar-2022  Wayne Shih              Add tests for TweetPhotos model
# 30-Mar-2022  Wayne Shih              Add more tests for TweetPhotos model
# 26-May-2022  Wayne Shih              Add clear cache before each test
# 28-May-2022  Wayne Shih              Add a test to test redis cache
# 28-May-2022  Wayne Shih              Add tests to user tweets cache
# $HISTORY$
# =================================================================================================


from datetime import date, timedelta

from django.core.files.uploadedfile import SimpleUploadedFile

from testing.testcases import TestCase
from tweets.models import Tweet, TweetPhoto
from tweets.services import TweetService
from twitter.caches import USER_TWEETS_PATTERN
from utils.redis_client import RedisClient
from utils.redis_serializers import DjangoModelSerializer
from utils.time_helpers import utc_now


class TweetTests(TestCase):

    def setUp(self):
        self.clear_cache()

        self.lbj23 = self.create_user(username='cavs_lbj23')
        self.kb24 = self.create_user(username='kobe24')
        self.sc30 = self.create_user(username='curry', password='sc30')

    def test_hours_to_now(self):
        user = self.create_user(username='kd')
        tweet = self.create_tweet(user=user, content='kd is MVP!')
        tweet.created_at = utc_now() - timedelta(hours=10)
        tweet.save()
        self.assertEqual(tweet.hours_to_now, 10)

    def test_tweet_model_attributes(self):
        self.assertEqual(hasattr(Tweet, 'id'), True)
        self.assertEqual(hasattr(Tweet, 'user'), True)
        self.assertEqual(hasattr(Tweet, 'user_id'), True)
        self.assertEqual(hasattr(Tweet, 'content'), True)
        self.assertEqual(hasattr(Tweet, 'created_at'), True)

    def test_tweet_model(self):
        user = self.sc30
        tweet = self.create_tweet(user=None, content='logo shot')

        self.assertEqual(tweet.user, None)
        self.assertEqual(tweet.created_at.day, date.today().day)

        tweet.delete()
        self.create_tweet(user=user, content='logo shot for 333333333!')

        user.delete()

        self.assertEqual(Tweet.objects.all().count(), 1)
        self.assertEqual(Tweet.objects.first().user, None)
        self.assertEqual(Tweet.content.field.max_length, 255)

    def test_auto_now_add(self):
        tweet = self.create_tweet(user=None, content='original tweet')
        old_created_time = tweet.created_at
        tweet.content = 'updated tweet'
        tweet.save()
        self.assertEqual(old_created_time, tweet.created_at)

    def test_str(self):
        user = self.lbj23
        tweet = self.create_tweet(user=user, content='I am the King')
        # print(tweet)
        self.assertEqual(str(tweet.created_at) in str(tweet), True)
        self.assertEqual(tweet.user.username in str(tweet), True)
        self.assertEqual(tweet.content in str(tweet), True)

    def test_like_set(self):
        tweet = self.create_tweet(user=self.lbj23, content='This is for u!')
        self.create_like(self.lbj23, tweet)
        self.assertEqual(tweet.like_set.count(), 1)

        self.create_like(self.lbj23, tweet)
        self.assertEqual(tweet.like_set.count(), 1)

        self.create_like(self.kb24, tweet)
        self.create_like(self.sc30, tweet)
        self.assertEqual(tweet.like_set.count(), 3)

    def test_like_str(self):
        tweet = self.create_tweet(user=self.lbj23, content='This is for u!')
        like = self.create_like(self.lbj23, tweet)

        # print(like)
        self.assertEqual(str(like.created_at) in str(like), True)
        self.assertEqual(like.user.username in str(like), True)
        self.assertEqual(str(like.content_type) in str(like), True)
        self.assertEqual(str(like.object_id) in str(like), True)


class TweetPhotoTests(TestCase):

    def setUp(self):
        self.lbj23 = self.create_user(username='cavs_lbj23')
        self.lbj23_tweet = self.create_tweet(self.lbj23, 'This is 4 u!')
        self.kb24 = self.create_user(username='kobe24')
        self.sc30 = self.create_user(username='curry', password='sc30')

    def test_tweet_photo_model_attributes(self):
        self.assertEqual(hasattr(TweetPhoto, 'id'), True)
        self.assertEqual(hasattr(TweetPhoto, 'tweet'), True)
        self.assertEqual(hasattr(TweetPhoto, 'tweet_id'), True)
        self.assertEqual(hasattr(TweetPhoto, 'user'), True)
        self.assertEqual(hasattr(TweetPhoto, 'user_id'), True)
        self.assertEqual(hasattr(TweetPhoto, 'file'), True)
        self.assertEqual(hasattr(TweetPhoto, 'created_at'), True)
        self.assertEqual(hasattr(TweetPhoto, 'status'), True)
        self.assertEqual(hasattr(TweetPhoto, 'order'), True)
        self.assertEqual(hasattr(TweetPhoto, 'has_deleted'), True)
        self.assertEqual(hasattr(TweetPhoto, 'deleted_at'), True)

    def test_tweet_photo_model(self):
        self.assertEqual(TweetPhoto.objects.all().count(), 0)
        self.assertEqual(self.lbj23_tweet.tweetphoto_set.count(), 0)
        photo = TweetPhoto.objects.create(
            tweet=self.lbj23_tweet,
            user=self.lbj23,
            file=SimpleUploadedFile(
                name='king-tweet-photo.jpg',
                content=str.encode('GOAT image'),
                content_type='image/jpeg',
            ),
        )
        self.assertEqual(TweetPhoto.objects.all().count(), 1)
        self.assertEqual(self.lbj23_tweet.tweetphoto_set.count(), 1)
        self.assertEqual(photo.user, self.lbj23)
        self.assertEqual(photo.tweet, self.lbj23_tweet)
        self.assertEqual('king-tweet-photo' in str(photo.file), True)
        self.assertEqual(photo.created_at.day, date.today().day)

    def test_str(self):
        photo = TweetPhoto.objects.create(
            tweet=self.lbj23_tweet,
            user=self.lbj23,
            file=SimpleUploadedFile(
                name='goat-tweet-photo.jpg',
                content=str.encode('GOAT image'),
                content_type='image/jpeg',
            ),
        )
        message = 'TweetPhoto-[{id}] in tweet-[{tweet_id}] by [{user}]-[{user_id}] ' \
                  'with order-[{order}] created at [{created_at}].\n' \
                  'File: [{file}]'
        self.assertEqual(message.format(
            id=photo.id,
            tweet_id=photo.tweet_id,
            user=photo.user,
            user_id=photo.user_id,
            order=photo.order,
            created_at=photo.created_at,
            file=photo.file,
        ), str(photo))


class TweetCacheTests(TestCase):

    def setUp(self):
        self.clear_cache()

        self.lbj23 = self.create_user(username='cavs_lbj23')
        self.kb24 = self.create_user(username='kobe24')
        self.sc30 = self.create_user(username='curry', password='sc30')

    def test_cache_tweet_in_redis(self):
        # test serialize/deserialize tweet to/from cache  <Wayne Shih> 29-May-2022
        tweet = self.create_tweet(user=self.sc30, content='logo shot')
        serialized_tweet = DjangoModelSerializer.serialize(tweet)
        conn = RedisClient.get_connection()
        conn.set(f'tweet:{tweet.id}', serialized_tweet)
        data = conn.get(f'tweet:{tweet.id}')
        cached_tweet = DjangoModelSerializer.deserialize(data)
        self.assertEqual(cached_tweet, tweet)

        # test serialize/deserialize None object to/from cache  <Wayne Shih> 29-May-2022
        non_existing_tweet_id = -1
        tweet = Tweet.objects.filter(id=non_existing_tweet_id).first()
        serialized_tweet = DjangoModelSerializer.serialize(tweet)
        data = conn.get(f'tweet:{non_existing_tweet_id}')
        cached_tweet = DjangoModelSerializer.deserialize(data)
        self.assertEqual(tweet, None)
        self.assertEqual(serialized_tweet, None)
        self.assertEqual(data, None)
        self.assertEqual(cached_tweet, None)

    def test_get_user_tweets(self):
        tweet_ids = []
        for i in range(3):
            tweet = self.create_tweet(self.sc30, f'logo shot - {i}')
            tweet_ids.append(tweet.id)
        tweet_ids = tweet_ids[::-1]

        # test cache miss  <Wayne Shih> 29-May-2022
        conn = RedisClient.get_connection()
        key_sc30 = USER_TWEETS_PATTERN.format(user_id=self.sc30.id)
        key_lbj23 = USER_TWEETS_PATTERN.format(user_id=self.lbj23.id)
        RedisClient.clear()
        self.assertEqual(conn.exists(key_sc30), False)
        self.assertEqual(conn.exists(key_lbj23), False)

        sc30_tweets = TweetService.get_cached_tweets(self.sc30.id)
        lbj23_tweets = TweetService.get_cached_tweets(self.lbj23.id)
        self.assertEqual(type(sc30_tweets), list)
        self.assertEqual(type(lbj23_tweets), list)
        self.assertEqual(conn.exists(key_sc30), True)
        self.assertEqual(conn.exists(key_lbj23), False)
        self.assertEqual([tweet.id for tweet in sc30_tweets], tweet_ids)
        self.assertEqual(len(lbj23_tweets), 0)

        # test cache hit  <Wayne Shih> 29-May-2022
        self.assertEqual(conn.exists(key_sc30), True)
        sc30_tweets = TweetService.get_cached_tweets(self.sc30.id)
        self.assertEqual(type(sc30_tweets), list)
        self.assertEqual([tweet.id for tweet in sc30_tweets], tweet_ids)
        self.assertEqual(conn.exists(key_sc30), True)

        # test push tweet to cache while key exists  <Wayne Shih> 29-May-2022
        self.assertEqual(conn.exists(key_sc30), True)
        new_sc30_tweet = self.create_tweet(self.sc30, 'logo shot - new')
        tweet_ids.insert(0, new_sc30_tweet.id)
        self.assertEqual(conn.exists(key_sc30), True)

        sc30_tweets = TweetService.get_cached_tweets(self.sc30.id)
        self.assertEqual(type(sc30_tweets), list)
        self.assertEqual([tweet.id for tweet in sc30_tweets], tweet_ids)

        # test push tweet to cache while key does NOT exist  <Wayne Shih> 29-May-2022
        RedisClient.clear()
        self.assertEqual(conn.exists(key_lbj23), False)
        new_lbj23_tweet = self.create_tweet(self.lbj23, 'king')
        tweet_ids.insert(0, new_lbj23_tweet.id)
        self.assertEqual(conn.exists(key_lbj23), True)

        lbj23_tweets = TweetService.get_cached_tweets(self.lbj23.id)
        self.assertEqual(type(lbj23_tweets), list)
        self.assertEqual([tweet.id for tweet in lbj23_tweets], [new_lbj23_tweet.id])
