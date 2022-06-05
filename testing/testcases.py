# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#           Make all unit tests are inherited from this class
#           so that all unit tests can share common methods
#
# =================================================================================================
#    Date      Name                    Description of Change
# 06-Sep-2021  Wayne Shih              Initial create: Refactor TestCase
# 07-Sep-2021  Wayne Shih              Correct comments
# 10-Oct-2021  Wayne Shih              React to pylint checks
# 04-Nov-2021  Wayne Shih              Add anonymous_client
# 04-Nov-2021  Wayne Shih              Add create_comment
# 24-Feb-2022  Wayne Shih              Add create_like
# 26-Feb-2022  Wayne Shih              Add create_user_and_auth_client
# 12-Mar-2022  Wayne Shih              Add create_newsfeed
# 23-Mar-2022  Wayne Shih              Add get_avator_url
# 30-Apr-2022  Wayne Shih              Add clear_cache
# 28-May-2022  Wayne Shih              Add clear redis up
# 30-May-2022  Wayne Shih              React to utils file structure refactor
# 05-Jun-2022  Wayne Shih              Add create_friendship
# $HISTORY$
# =================================================================================================


from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.cache import caches
from django.test import TestCase as DjangoTestCase
from rest_framework.test import APIClient

from comments.models import Comment
from friendships.models import Friendship
from likes.models import Like
from newsfeeds.models import NewsFeed
from tweets.models import Tweet
from utils.caches.redis_client import RedisClient


class TestCase(DjangoTestCase):

    @property
    def anonymous_client(self):
        if not hasattr(self, '_anonymous_client'):
            self._anonymous_client = APIClient()
        return self._anonymous_client

    def create_user(self, username, email=None, password=None):
        if password is None:
            password = 'default_generic_password'
        if email is None:
            email = f'{username}@django-twitter.com'

        # <Wayne Shih> 12-Aug-2021
        # Don't use User.objects.create() to create users
        # because password needs to be hashed, also username and email need to be normalized
        # (e.g. trim).
        return User.objects.create_user(username, email, password)

    def create_tweet(self, user, content=None):
        if content is None:
            content = 'Default content -- Welcome to Django-Twitter'
        return Tweet.objects.create(user=user, content=content)

    def create_comment(self, user, tweet, content=None):
        if content is None:
            content = 'Default content -- Welcome to Django-Twitter'
        return Comment.objects.create(user=user, tweet=tweet, content=content)

    def create_like(self, user, target):
        # <Wayne Shih> 24-Feb-2022
        # target is tweet or comment.
        # content_type is recorded in django_content_type table.
        # get_for_model() here is to get model's metadata so that db knows the model.
        #   - https://docs.djangoproject.com/en/4.0/ref/contrib/contenttypes/#django.contrib.contenttypes.models.ContentTypeManager.get_for_model
        instance, _ = Like.objects.get_or_create(
            user=user,
            content_type=ContentType.objects.get_for_model(target.__class__),
            object_id=target.id,
        )
        return instance

    def create_user_and_auth_client(self, *args, **kwargs):
        user = self.create_user(*args, **kwargs)
        client = APIClient()
        client.force_authenticate(user)
        return user, client

    def create_newsfeed(self, user, tweet):
        return NewsFeed.objects.create(user=user, tweet=tweet)

    def create_friendship(self, from_user, to_user):
        return Friendship.objects.create(from_user=from_user, to_user=to_user)

    def get_avator_url(self, user):
        return user.profile.avatar.url if user.profile.avatar else None

    def clear_cache(self):
        caches['testing'].clear()
        RedisClient.clear()
