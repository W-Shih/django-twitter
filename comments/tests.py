# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#           comment model unit tests
#
# =================================================================================================
#    Date      Name                    Description of Change
# 05-Nov-2021  Wayne Shih              Initial create
# 27-Nov-2021  Wayne Shih              React to  Comment ordering update
# 24-Feb-2022  Wayne Shih              Add tests for likes model
# 20-Mar-2022  Wayne Shih              Change class name to CommentTests
# $HISTORY$
# =================================================================================================


import re

from comments.models import Comment
from testing.testcases import TestCase


class CommentTests(TestCase):

    def setUp(self):
        self.lbj23 = self.create_user(username='cavs_lbj23')
        self.tweet = self.create_tweet(user=self.lbj23, content='This is for u!')
        self.kobe24 = self.create_user(username='kobe24')
        self.kobe24_comment = self.create_comment(
            user=self.kobe24,
            tweet=self.tweet,
            content='Good job, my bro',
        )

    def test_comment_model_attributes(self):
        self.assertEqual(hasattr(Comment, 'id'), True)
        self.assertEqual(hasattr(Comment, 'user_id'), True)
        self.assertEqual(hasattr(Comment, 'user'), True)
        self.assertEqual(hasattr(Comment, 'tweet_id'), True)
        self.assertEqual(hasattr(Comment, 'tweet'), True)
        self.assertEqual(hasattr(Comment, 'content'), True)
        self.assertEqual(hasattr(Comment, 'created_at'), True)
        self.assertEqual(hasattr(Comment, 'updated_at'), True)

    def test_comment_model(self):
        comment = self.create_comment(
            user=None,
            tweet=self.tweet,
            content='I am glad that I was there!!',
        )
        comments = Comment.objects.all()
        self.assertEqual(comments.count(), 2)
        # <Wayne Shih> 27-Nov-2021
        # test order by 'created_at'
        self.assertEqual(comments.last().user, None)
        self.assertEqual(comments.last().content, comment.content)
        self.assertEqual(comments.last().created_at > self.kobe24_comment.updated_at, True)

        self.assertEqual(hasattr(self.kobe24, 'comment_set'), True)
        self.assertEqual(hasattr(self.tweet, 'comment_set'), True)

    def test_comment_meta(self):
        self.assertEqual(len(Comment._meta.index_together), 1)
        self.assertEqual(len(Comment._meta.ordering), 1)

        self.assertEqual(
            bool(re.search('tweet(.*?)created_at', str(Comment._meta.index_together))),
            True
        )
        self.assertEqual(Comment._meta.ordering, ('created_at',))

    def test_comment_on_delete(self):
        self.kobe24.delete()
        self.assertEqual(Comment.objects.first().user, None)
        self.tweet.delete()
        self.assertEqual(Comment.objects.first().tweet, None)

    def test_time(self):
        old_created_time = self.kobe24_comment.created_at
        old_updated_time = self.kobe24_comment.updated_at
        self.kobe24_comment.tweet = None
        self.kobe24_comment.save()
        self.assertEqual(old_created_time, self.kobe24_comment.created_at)
        self.assertEqual(old_updated_time < self.kobe24_comment.updated_at, True)

    def test_comment_str(self):
        self.assertEqual(
            str(self.kobe24_comment.created_at) in str(self.kobe24_comment),
            True
        )
        self.assertEqual(
            str(self.kobe24_comment.user_id) in str(self.kobe24_comment),
            True
        )
        self.assertEqual(
            str(self.kobe24_comment.tweet_id) in str(self.kobe24_comment),
            True
        )
        message = '{created_at}, {user}-{user_id} says "{content}" on tweet-{tweet_id}'
        self.assertEqual(message.format(
            created_at=self.kobe24_comment.created_at,
            user=self.kobe24_comment.user,
            user_id=self.kobe24_comment.user_id,
            content=self.kobe24_comment.content,
            tweet_id=self.kobe24_comment.tweet_id,
        ), str(self.kobe24_comment))

    def test_like_set(self):
        self.create_like(self.lbj23, self.kobe24_comment)
        self.assertEqual(self.kobe24_comment.like_set.count(), 1)

        self.create_like(self.lbj23, self.kobe24_comment)
        self.assertEqual(self.kobe24_comment.like_set.count(), 1)

        self.create_like(self.kobe24, self.kobe24_comment)
        self.assertEqual(self.kobe24_comment.like_set.count(), 2)

    def test_like_str(self):
        like = self.create_like(self.lbj23, self.kobe24_comment)

        # print(like)
        self.assertEqual(like.user.username in str(like), True)
        self.assertEqual(str(like.created_at) in str(like), True)
        self.assertEqual(str(like.content_type) in str(like), True)
        self.assertEqual(str(like.object_id) in str(like), True)
