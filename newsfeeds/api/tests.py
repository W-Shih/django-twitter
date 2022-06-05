# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#           newsfeed api unit tests
#
# =================================================================================================
#    Date      Name                    Description of Change
# 04-Nov-2021  Wayne Shih              Initial create
# 27-Apr-2022  Wayne Shih              Add tests for newfeed list endless pagination
# 29-Apr-2022  Wayne Shih              React to deprecating key in newsfeeds list api
# 26-May-2022  Wayne Shih              Add a test to test cached user
# 26-May-2022  Wayne Shih              Add a test to test cached tweet
# 05-Jun-2022  Wayne Shih              Add test for only caching REDIS_LIST_SIZE_LIMIT in redis
# $HISTORY$
# =================================================================================================


from urllib import parse

from django.conf import settings
from rest_framework import status
from rest_framework.test import APIClient

from newsfeeds.models import NewsFeed
from newsfeeds.services import NewsFeedService
from testing.testcases import TestCase
from utils.pagination import EndlessPagination


FOLLOW_URL = '/api/friendships/{}/follow/'
NEWSFEED_LIST_URL = '/api/newsfeeds/'
TWEET_CREATE_URL = '/api/tweets/'


class NewsFeedApiTests(TestCase):

    def setUp(self):
        self.clear_cache()

        self.lbj23 = self.create_user('lbj23')
        self.lbj23_client = APIClient()
        self.lbj23_client.force_authenticate(self.lbj23)

        self.kobe24 = self.create_user('kobe24')
        self.kobe24_client = APIClient()
        self.kobe24_client.force_authenticate(self.kobe24)

    def test_list_api(self):
        # test not log-in
        response = self.anonymous_client.get(NEWSFEED_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # test http POST instead of GET
        response = self.lbj23_client.post(NEWSFEED_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # test authenticated user with GET
        response = self.lbj23_client.get(NEWSFEED_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

        # test seeing user's own tweet
        self.lbj23_client.post(TWEET_CREATE_URL, {'content': 'I am the King James!'})
        response = self.lbj23_client.get(NEWSFEED_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

        # able to see someone's tweet after following
        self.lbj23_client.post(FOLLOW_URL.format(self.kobe24.id))
        self.kobe24_client.post(TWEET_CREATE_URL, {'content': 'Be Better!'})
        response = self.lbj23_client.get(NEWSFEED_LIST_URL)
        newsfeeds = response.data['results']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(newsfeeds), 2)
        self.assertEqual(newsfeeds[0]['created_at'] > newsfeeds[1]['created_at'], True)

    def test_list_pagination(self):
        page_size = EndlessPagination.page_size

        newsfeeds = []
        num_newsfeeds = page_size * 2 - 1
        for i in range(num_newsfeeds):
            tweet = self.create_tweet(self.kobe24, f'kb24::tweet::{i}')
            newsfeed = self.create_newsfeed(self.lbj23, tweet)
            newsfeeds.append(newsfeed)
        newsfeeds = newsfeeds[::-1]

        # Test the first page of lbj23's newsfeeds  <Wayne Shih> 27-Apr-2022
        response = self.lbj23_client.get(NEWSFEED_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['has_next'], True)
        self.assertEqual(response.data['results'][0]['id'], newsfeeds[0].id)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(
            response.data['results'][page_size - 1]['id'],
            newsfeeds[page_size - 1].id
        )
        self.assertEqual(
            str(newsfeeds[page_size - 1].created_at.time()) in parse.unquote(response.data['next']),
            True
        )
        self.assertEqual(
            str(newsfeeds[page_size - 1].created_at.date()) in parse.unquote(response.data['next']),
            True
        )

        # Test the second/last page of lbj23's newsfeeds  <Wayne Shih> 27-Apr-2022
        response = self.lbj23_client.get(NEWSFEED_LIST_URL, {
            'created_at__lt': newsfeeds[page_size - 1].created_at,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['has_next'], False)
        self.assertEqual(response.data['next'], None)
        self.assertEqual(len(response.data['results']), page_size - 1)
        self.assertEqual(response.data['results'][0]['id'], newsfeeds[page_size].id)
        self.assertEqual(
            response.data['results'][page_size - 2]['id'],
            newsfeeds[page_size * 2 - 2].id
        )

        # Test lbj23's new newsfeeds  <Wayne Shih> 27-Apr-2022
        response = self.lbj23_client.get(NEWSFEED_LIST_URL, {
            'created_at__gt': newsfeeds[0].created_at,
        })
        self.assertEqual(response.data['has_next'], False)
        self.assertEqual(response.data['next'], None)
        self.assertEqual(len(response.data['results']), 0)

        new_tweet1 = self.create_tweet(self.lbj23, 'lbj23::new_tweet::1')
        new_tweet2 = self.create_tweet(self.lbj23, 'lbj23::new_tweet::2')
        new_newsfeed1 = self.create_newsfeed(self.lbj23, new_tweet1)
        new_newsfeed2 = self.create_newsfeed(self.lbj23, new_tweet2)
        response = self.lbj23_client.get(NEWSFEED_LIST_URL, {
            'created_at__gt': newsfeeds[0].created_at,
        })
        self.assertEqual(response.data['has_next'], False)
        self.assertEqual(response.data['next'], None)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['id'], new_newsfeed2.id)
        self.assertEqual(response.data['results'][1]['id'], new_newsfeed1.id)

    def test_cached_user(self):
        profile = self.kobe24.profile
        profile.nickname = 'lakers_24'
        profile.save()
        self.create_newsfeed(self.lbj23, self.create_tweet(self.kobe24, 'tweet1'))
        self.create_newsfeed(self.lbj23, self.create_tweet(self.kobe24, 'tweet2'))

        # <Wayne Shih> see user kobe24 and his profile
        response = self.lbj23_client.get(NEWSFEED_LIST_URL)
        newsfeeds = response.data['results']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(newsfeeds[0]['tweet']['user']['username'], 'kobe24')  # user cache miss
        self.assertEqual(newsfeeds[0]['tweet']['user']['nickname'], 'lakers_24')  # profile cache miss
        self.assertEqual(newsfeeds[1]['tweet']['user']['username'], 'kobe24')  # cache hit
        self.assertEqual(newsfeeds[1]['tweet']['user']['nickname'], 'lakers_24')  # profile cache hit

        # <Wayne Shih> see kobe24's new username
        self.kobe24.username = 'kobe0824'
        self.kobe24.save()
        response = self.lbj23_client.get(NEWSFEED_LIST_URL)
        newsfeeds = response.data['results']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(newsfeeds[0]['tweet']['user']['username'], 'kobe0824')  # user cache miss
        self.assertEqual(newsfeeds[0]['tweet']['user']['nickname'], 'lakers_24')  # profile cache hit
        self.assertEqual(newsfeeds[1]['tweet']['user']['username'], 'kobe0824')  # user cache hit
        self.assertEqual(newsfeeds[1]['tweet']['user']['nickname'], 'lakers_24')  # profile cache hit

        # <Wayne Shih> see kobe24's new nickname
        profile.nickname = 'lakers_kb0824'
        profile.save()
        response = self.lbj23_client.get(NEWSFEED_LIST_URL)
        newsfeeds = response.data['results']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(newsfeeds[0]['tweet']['user']['username'], 'kobe0824')  # user cache hit
        self.assertEqual(newsfeeds[0]['tweet']['user']['nickname'], 'lakers_kb0824')  # profile cache miss
        self.assertEqual(newsfeeds[1]['tweet']['user']['username'], 'kobe0824')  # user cache hit
        self.assertEqual(newsfeeds[1]['tweet']['user']['nickname'], 'lakers_kb0824')  # profile cache hit

    def test_cached_tweets(self):
        kobe24_tweet1 = self.create_tweet(self.kobe24, 'content1')
        kobe24_tweet2 = self.create_tweet(self.kobe24, 'content2')
        self.create_newsfeed(self.kobe24, kobe24_tweet1)
        self.create_newsfeed(self.kobe24, kobe24_tweet2)
        self.create_newsfeed(self.lbj23, kobe24_tweet1)
        self.create_newsfeed(self.lbj23, kobe24_tweet2)

        # <Wayne Shih> see kobe24's tweets
        response = self.kobe24_client.get(NEWSFEED_LIST_URL)
        newsfeeds = response.data['results']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(newsfeeds[0]['tweet']['user']['username'], 'kobe24')  # user cache miss
        self.assertEqual(newsfeeds[0]['tweet']['content'], 'content2')  # tweet miss
        self.assertEqual(newsfeeds[1]['tweet']['user']['username'], 'kobe24')  # user cache hit
        self.assertEqual(newsfeeds[1]['tweet']['content'], 'content1')  # tweet miss

        response = self.lbj23_client.get(NEWSFEED_LIST_URL)
        newsfeeds = response.data['results']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(newsfeeds[0]['tweet']['user']['username'], 'kobe24')  # user cache hit
        self.assertEqual(newsfeeds[0]['tweet']['content'], 'content2')  # tweet hit
        self.assertEqual(newsfeeds[1]['tweet']['user']['username'], 'kobe24')  # user cache hit
        self.assertEqual(newsfeeds[1]['tweet']['content'], 'content1')  # tweet hit

        # <Wayne Shih> see kobe24's new tweet1
        kobe24_tweet2.content = 'new_content2'
        kobe24_tweet2.save()
        response = self.kobe24_client.get(NEWSFEED_LIST_URL)
        newsfeeds = response.data['results']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(newsfeeds[0]['tweet']['user']['username'], 'kobe24')  # user cache hit
        self.assertEqual(newsfeeds[0]['tweet']['content'], 'new_content2')  # tweet miss
        self.assertEqual(newsfeeds[1]['tweet']['user']['username'], 'kobe24')  # user cache hit
        self.assertEqual(newsfeeds[1]['tweet']['content'], 'content1')  # tweet hit

        response = self.lbj23_client.get(NEWSFEED_LIST_URL)
        newsfeeds = response.data['results']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(newsfeeds[0]['tweet']['user']['username'], 'kobe24')  # user cache hit
        self.assertEqual(newsfeeds[0]['tweet']['content'], 'new_content2')  # tweet hit
        self.assertEqual(newsfeeds[1]['tweet']['user']['username'], 'kobe24')  # user cache hit
        self.assertEqual(newsfeeds[1]['tweet']['content'], 'content1')  # tweet hit

        # <Wayne Shih> see kobe24's new username
        self.kobe24.username = 'kobe0824'
        self.kobe24.save()
        response = self.kobe24_client.get(NEWSFEED_LIST_URL)
        newsfeeds = response.data['results']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(newsfeeds[0]['tweet']['user']['username'], 'kobe0824')  # user cache miss
        self.assertEqual(newsfeeds[0]['tweet']['content'], 'new_content2')  # tweet miss
        self.assertEqual(newsfeeds[1]['tweet']['user']['username'], 'kobe0824')  # user cache hit
        self.assertEqual(newsfeeds[1]['tweet']['content'], 'content1')  # tweet hit

        response = self.lbj23_client.get(NEWSFEED_LIST_URL)
        newsfeeds = response.data['results']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(newsfeeds[0]['tweet']['user']['username'], 'kobe0824')  # user cache hit
        self.assertEqual(newsfeeds[0]['tweet']['content'], 'new_content2')  # tweet hit
        self.assertEqual(newsfeeds[1]['tweet']['user']['username'], 'kobe0824')  # user cache hit
        self.assertEqual(newsfeeds[1]['tweet']['content'], 'content1')  # tweet hit

    def _get_all_paginated_newsfeeds(self, client):
        response = client.get(NEWSFEED_LIST_URL)
        results = response.data['results']
        while response.data['has_next']:
            response = client.get(NEWSFEED_LIST_URL, {
                'created_at__lt': results[-1]['created_at'],
            })
            results.extend(response.data['results'])
        return results

    def test_redis_list_size_limit(self):
        page_size = EndlessPagination.page_size
        max_page_size = EndlessPagination.max_page_size
        list_size_limit = settings.REDIS_LIST_SIZE_LIMIT

        users = [self.create_user(f'user::{i}') for i in range(5)]
        newsfeeds = []
        num_newsfeeds = list_size_limit + page_size
        self.assertEqual(num_newsfeeds > max_page_size, True)
        for i in range(num_newsfeeds):
            user = users[i % 5]
            tweet = self.create_tweet(user, f'{user.username}::tweet::{i}')
            newsfeed = self.create_newsfeed(self.lbj23, tweet)
            newsfeeds.append(newsfeed)
        newsfeeds = newsfeeds[::-1]

        # Test cached list and qs size  <Wayne Shih> 04-Jun-2022
        cached_newsfeeds = NewsFeedService.get_cached_newsfeeds(self.lbj23.id)
        qs_newsfeeds = NewsFeed.objects.filter(user_id=self.lbj23.id)
        self.assertEqual(len(cached_newsfeeds), list_size_limit)
        self.assertEqual(qs_newsfeeds.count(), num_newsfeeds)

        # Test get all newsfeeds via api  <Wayne Shih> 04-Jun-2022
        results = self._get_all_paginated_newsfeeds(self.lbj23_client)
        self.assertEqual(len(results), num_newsfeeds)
        for i in range(num_newsfeeds):
            self.assertEqual(results[i]['id'], newsfeeds[i].id)

        # Test max page size  <Wayne Shih> 04-Jun-2022
        query_params = {'page_size': num_newsfeeds * 2}
        response = self.lbj23_client.get(NEWSFEED_LIST_URL, query_params)
        page_last_feed_created_at = str(newsfeeds[max_page_size - 1].created_at.astimezone())\
            .replace(' ', 'T')\
            .replace('+00:00', 'Z')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['has_next'], True)
        self.assertEqual(len(response.data['results']), max_page_size)
        for i in range(max_page_size):
            self.assertEqual(results[i]['id'], newsfeeds[i].id)
        self.assertEqual(
            page_last_feed_created_at in parse.unquote(response.data['next']),
            True
        )

        # Test add new feeds  <Wayne Shih> 04-Jun-2022
        self.create_friendship(self.lbj23, self.kobe24)
        kb_tweet = self.create_tweet(self.kobe24, 'kb new tweet')
        NewsFeedService.fanout_to_followers(kb_tweet)

        def _test_newsfeeds_after_new_feed_pushed():
            results = self._get_all_paginated_newsfeeds(self.lbj23_client)
            self.assertEqual(len(results), num_newsfeeds + 1)
            self.assertEqual(results[0]['tweet']['id'], kb_tweet.id)
            for i in range(num_newsfeeds):
                self.assertEqual(results[i + 1]['id'], newsfeeds[i].id)

        _test_newsfeeds_after_new_feed_pushed()

        # Test cache has been clear  <Wayne Shih> 04-Jun-2022
        self.clear_cache()
        _test_newsfeeds_after_new_feed_pushed()

        self.clear_cache()
        query_params = {'created_at__gt': newsfeeds[0].created_at}
        response = self.lbj23_client.get(NEWSFEED_LIST_URL, query_params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['next'], None)
        self.assertEqual(response.data['has_next'], False)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['tweet']['id'], kb_tweet.id)
