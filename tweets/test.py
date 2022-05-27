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
# $HISTORY$
# =================================================================================================


from datetime import date, timedelta

from django.core.files.uploadedfile import SimpleUploadedFile

from testing.testcases import TestCase
from tweets.models import Tweet, TweetPhoto
from utils.time_helpers import utc_now


class TweetTest(TestCase):

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


class TweetPhotoTest(TestCase):

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
