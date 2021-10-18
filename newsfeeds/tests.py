# =================================================================================================
# File description:
#           Newsfeed model unit tests
#
# =================================================================================================
#    Date      Name                    Description of Change
# 17-Oct-2021  Wayne Shih              Initial create
# $HISTORY$
# =================================================================================================


import re

from testing.testcases import TestCase
from newsfeeds.models import NewsFeed


class NewsfeedTest(TestCase):

    def setUp(self):
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

    def test_comment_on_delete(self):
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

        message = '-- {created_at} inbox of {user}: {tweet} --'.format(
            created_at=self.newsfeed.created_at,
            user=self.newsfeed.user,
            tweet=self.newsfeed.tweet,
        )
        self.assertEqual(message, str(self.newsfeed))
