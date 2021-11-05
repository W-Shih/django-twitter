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
# $HISTORY$
# =================================================================================================


from django.test import TestCase as DjangoTestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from tweets.models import Tweet


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
