# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#           tweets api unit tests
#
# =================================================================================================
#    Date      Name                    Description of Change
# 06-Sep-2021  Wayne Shih              Initial create
# 10-Oct-2021  Wayne Shih              React to pylint checks
# 04-Nov-2021  Wayne Shih              React to adding anonymous_client to base class
# 06-Nov-2021  Wayne Shih              Modify some assertEqual to check set instead of list
# 27-Nov-2021  Wayne Shih              Add tests for tweet retrieve api
# 27-Nov-2021  Wayne Shih              React to decorator enhancement
# 23-Feb-2022  Wayne Shih              Add a test for tweet list api
# 12-Mar-2022  Wayne Shih              React to serializer changes
# 23-Mar-2022  Wayne Shih              React to user-related serializer changes
# 30-Mar-2022  Wayne Shih              React to adding tweet photo and add tests for tweet photo
# 26-Apr-2022  Wayne Shih              Add tests for tweet list endless pagination
# 27-Apr-2022  Wayne Shih              React to renaming to EndlessPagination
# $HISTORY$
# =================================================================================================


from urllib import parse

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APIClient

from testing.testcases import TestCase
from utils.pagination import EndlessPagination
from tweets.models import Tweet, TweetPhoto


TWEET_LIST_URL = '/api/tweets/'
TWEET_CREATE_URL = '/api/tweets/'
TWEET_RETRIEVE_URL = '/api/tweets/{}/'


class TweetApiTests(TestCase):

    # <Wayne Shih> 06-Sep-2021
    # This method will be executed before executing each test method
    def setUp(self):
        self.user1 = self.create_user(username='lbj23')
        self.tweets1 = [
            self.create_tweet(self.user1)
            for _ in range(3)
        ]
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

        self.user2 = self.create_user(username='kd35')
        self.tweets2 = [
            self.create_tweet(self.user2)
            for _ in range(2)
        ]

    # <Wayne Shih> 06-Sep-2021
    # The name of each test method must start with 'test_'.
    def test_list_api(self):
        response = self.anonymous_client.get(TWEET_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')
        errors_str = 'Request is missing param(s): user_id. ' \
                     'All missing params are required to provide.'
        self.assertEqual(response.data['errors'], errors_str)

        # Non-existing user id
        non_existing_user_id = -1
        response = self.anonymous_client.get(TWEET_LIST_URL, {
            'user_id': non_existing_user_id
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['tweets']), 0)

        response = self.anonymous_client.get(TWEET_LIST_URL, {'user_id': self.user1.id})
        tweets = response.data['tweets']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(isinstance(tweets, list), True)
        self.assertEqual(len(tweets), 3)
        self.assertEqual(
            set(tweets[0].keys()),
            {
                'id',
                'user',
                'created_at',
                'content',
                'comments_count',
                'has_liked',
                'likes_count',
                'photo_urls',
            }
        )
        # <Wayne Shih> 06-Sep-2021
        # test order by '-created_at'
        for index in range(len(tweets) - 1):
            self.assertEqual(
                tweets[index]['created_at'] > tweets[index + 1]['created_at'],
                True
            )

        response = self.anonymous_client.get(TWEET_LIST_URL, {'user_id': self.user2.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['tweets']), 2)
        # <Wayne Shih> 06-Sep-2021
        # test order by '-created_at'
        self.assertEqual(response.data['tweets'][0]['id'], self.tweets2[1].id)
        self.assertEqual(response.data['tweets'][1]['id'], self.tweets2[0].id)
        self.assertEqual(
            response.data['tweets'][0]['created_at'] > response.data['tweets'][1]['created_at'],
            True
        )

    # <Wayne Shih> 28-Mar-2022
    # Test create a tweet without tweet photos
    def test_create_api(self):
        # <Wayne Shih> 28-Mar-2022
        # Not login user can't tweet
        response = self.anonymous_client.post(TWEET_CREATE_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # <Wayne Shih> 28-Mar-2022
        # Missing param(s): content
        response = self.user1_client.post(TWEET_CREATE_URL)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')

        # <Wayne Shih> 28-Mar-2022
        # content is too short
        response = self.user1_client.post(TWEET_CREATE_URL, {'content': '123'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')

        # <Wayne Shih> 28-Mar-2022
        # content is too long
        response = self.user1_client.post(TWEET_CREATE_URL, {
            'content': '1' * 256
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')

        # <Wayne Shih> 28-Mar-2022
        # Login user tweets successfully
        tweets_count = Tweet.objects.count()
        response = self.user1_client.post(TWEET_CREATE_URL, {
            'content': 'I am the King James!'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['id'], self.user1.id)
        self.assertEqual(response.data['content'], 'I am the King James!')
        self.assertEqual(Tweet.objects.count(), tweets_count + 1)
        self.assertEqual(response.data['user'], {
            'id': self.user1.id,
            'username': self.user1.username,
            'nickname': self.user1.profile.nickname,
            'avatar_url': self.get_avator_url(self.user1),
        })
        self.assertEqual(
            set(response.data.keys()),
            {
                'id',
                'user',
                'created_at',
                'content',
                'comments_count',
                'has_liked',
                'likes_count',
                'photo_urls',
            }
        )

    def test_create_with_photos(self):
        # <Wayne Shih> 28-Mar-2022
        # Login user tweets a photo without content
        response = self.user1_client.post(TWEET_CREATE_URL, {
            'photo_files': [
                SimpleUploadedFile(
                    name='photo-without-content.jpg',
                    content=str.encode('photo-without-content image'),
                    content_type='image/jpeg',
                ),
            ],
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')

        # <Wayne Shih> 28-Mar-2022
        # Test login user still compatible to tweet content only
        response = self.user1_client.post(TWEET_CREATE_URL, {'content': 'only content'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['id'], self.user1.id)
        self.assertEqual(response.data['content'], 'only content')
        self.assertEqual(TweetPhoto.objects.count(), 0)
        self.assertEqual(len(response.data['photo_urls']), 0)

        # <Wayne Shih> 28-Mar-2022
        # Test login user still compatible to tweet content only
        response = self.user1_client.post(TWEET_CREATE_URL, {
            'content': 'content with empty photo file list',
            'photo_files': []
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['id'], self.user1.id)
        self.assertEqual(response.data['content'], 'content with empty photo file list')
        self.assertEqual(len(response.data['photo_urls']), 0)
        self.assertEqual(TweetPhoto.objects.count(), 0)

        # <Wayne Shih> 28-Mar-2022
        # Login user tweets content with a photo
        response = self.user1_client.post(TWEET_CREATE_URL, {
            'content': 'Chasing the GOAT!!',
            'photo_files': [
                SimpleUploadedFile(
                    name='chasing-GOAT-photo.jpg',
                    content=str.encode('chasing-GOAT image'),
                    content_type='image/jpeg',
                ),
            ],
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['id'], self.user1.id)
        self.assertEqual(response.data['content'], 'Chasing the GOAT!!')
        self.assertEqual(len(response.data['photo_urls']), 1)
        self.assertEqual('chasing-GOAT-photo' in response.data['photo_urls'][0], True)

        # <Wayne Shih> 28-Mar-2022
        # Login user tweets content with 4 photos and
        # check photos order as uploaded
        response = self.user1_client.post(TWEET_CREATE_URL, {
            'content': 'My NBA titles',
            'photo_files': [
                SimpleUploadedFile(
                    name='my-titles-heat-1.jpg',
                    content=str.encode('my-titles-heat-1 image'),
                    content_type='image/jpeg',
                ),
                SimpleUploadedFile(
                    name='my-titles-heat-2.jpg',
                    content=str.encode('my-titles-heat-2 image'),
                    content_type='image/jpeg',
                ),
                SimpleUploadedFile(
                    name='my-titles-cavs.jpg',
                    content=str.encode('my-titles-cavs image'),
                    content_type='image/jpeg',
                ),
                SimpleUploadedFile(
                    name='my-titles-lakers.jpg',
                    content=str.encode('my-titles-lakers image'),
                    content_type='image/jpeg',
                ),
            ],
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['id'], self.user1.id)
        self.assertEqual(response.data['content'], 'My NBA titles')
        self.assertEqual(len(response.data['photo_urls']), 4)
        self.assertEqual('my-titles-heat-1' in response.data['photo_urls'][0], True)
        self.assertEqual('my-titles-heat-2' in response.data['photo_urls'][1], True)
        self.assertEqual('my-titles-cavs' in response.data['photo_urls'][2], True)
        self.assertEqual('my-titles-lakers' in response.data['photo_urls'][3], True)

        # <Wayne Shih> 28-Mar-2022
        # Login user tweets content with 5 photos
        photo_count = TweetPhoto.objects.count()
        response = self.user1_client.post(TWEET_CREATE_URL, {
            'content': 'lakers starters',
            'photo_files': [
                SimpleUploadedFile(
                    name=f'lakers-starters-{index}.jpg',
                    content=str.encode(f'lakers-starters-{index} image'),
                    content_type='image/jpeg',
                )
                for index in range(5)
            ],
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')
        self.assertEqual(
            response.data['errors']['photo_files'][0],
            'Ensure this field has no more than 4 elements.'
        )
        self.assertEqual(TweetPhoto.objects.count(), photo_count)

    def test_retrieve_api(self):
        # Non-existing tweet
        non_existing_tweet_id = -1
        url = TWEET_RETRIEVE_URL.format(non_existing_tweet_id)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Get tweet with 0 comment
        tweet = self.create_tweet(self.user1, 'This is for u!')
        url = TWEET_RETRIEVE_URL.format(tweet.id)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.json().keys()),
            {
                'id',
                'user',
                'created_at',
                'content',
                'comments_count',
                'has_liked',
                'likes_count',
                'comments',
                'likes',
                'photo_urls',
            }
        )
        self.assertEqual(
            response.json().get('user').keys(),
            {'id', 'username', 'nickname', 'avatar_url'}
        )
        self.assertEqual(isinstance(response.json().get('comments'), list), True)
        self.assertEqual(len(response.data['comments']), 0)

        # Get tweet with 3 comments
        self.create_comment(self.user1, tweet, 'Chasing the GOAT!')
        self.create_comment(self.user2, tweet, 'Good for u!')
        self.create_comment(
            self.user2,
            self.create_tweet(self.user2, 'another tweet'),
        )
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['comments']), 2)
        self.assertEqual(
            set(response.json().get('comments')[0].keys()),
            {'id', 'tweet_id', 'user', 'content', 'created_at', 'has_liked', 'likes_count'}
        )
        self.assertEqual(response.data['comments'][0]['user']['username'], self.user1.username)
        self.assertEqual(response.data['comments'][1]['user']['username'], self.user2.username)
        self.assertEqual(
            response.data['comments'][0]['created_at'] <
            response.data['comments'][1]['created_at'],
            True
        )

    def test_retrieve_with_photos(self):
        tweet_id = self.user1_client.post(TWEET_CREATE_URL, {
            'content': 'titles',
            'photo_files': [
                SimpleUploadedFile(
                    name='retrieve-titles-cavs.jpg',
                    content=str.encode('retrieve-titles-cavs image'),
                    content_type='image/jpeg',
                ),
                SimpleUploadedFile(
                    name='retrieve-titles-heat-1.jpg',
                    content=str.encode('retrieve-titles-heat-1 image'),
                    content_type='image/jpeg',
                ),
                SimpleUploadedFile(
                    name='retrieve-titles-lakers.jpg',
                    content=str.encode('retrieve-titles-lakers image'),
                    content_type='image/jpeg',
                ),
            ],
        }).data['id']

        url = TWEET_RETRIEVE_URL.format(tweet_id)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['photo_urls']), 3)
        self.assertEqual('retrieve-titles-cavs' in response.data['photo_urls'][0], True)
        self.assertEqual('retrieve-titles-heat-1' in response.data['photo_urls'][1], True)
        self.assertEqual('retrieve-titles-lakers' in response.data['photo_urls'][2], True)

    def test_list_pagination(self):
        page_size = EndlessPagination.page_size

        kb24 = self.create_user(username='kb24')
        tweets = []
        num_tweets = page_size * 3
        for i in range(num_tweets):
            tweet = self.create_tweet(kb24, f'kb24::tweet::{i}')
            tweets.append(tweet)
        tweets = tweets[::-1]

        # Test the first page of kb24's tweets  <Wayne Shih> 25-Apr-2022
        response = self.anonymous_client.get(TWEET_LIST_URL, {'user_id': kb24.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['has_next'], True)
        self.assertEqual(len(response.data['tweets']), page_size)
        self.assertEqual(response.data['tweets'][0]['id'], tweets[0].id)
        self.assertEqual(response.data['tweets'][page_size - 1]['id'], tweets[page_size - 1].id)
        self.assertEqual(
            str(tweets[page_size - 1].created_at.date()) in parse.unquote(response.data['next']),
            True
        )
        self.assertEqual(
            str(tweets[page_size - 1].created_at.time()) in parse.unquote(response.data['next']),
            True
        )

        # Test the second page of kb24's tweets  <Wayne Shih> 25-Apr-2022
        response = self.anonymous_client.get(TWEET_LIST_URL, {
            'user_id': kb24.id,
            'created_at__lt': tweets[page_size - 1].created_at,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['has_next'], True)
        self.assertEqual(
            str(tweets[page_size * 2 - 1].created_at.date())
            in parse.unquote(response.data['next']),
            True
        )
        self.assertEqual(
            str(tweets[page_size * 2 - 1].created_at.time())
            in parse.unquote(response.data['next']),
            True
        )
        self.assertEqual(len(response.data['tweets']), page_size)
        self.assertEqual(response.data['tweets'][0]['id'], tweets[page_size].id)
        self.assertEqual(response.data['tweets'][page_size - 1]['id'], tweets[page_size * 2 - 1].id)

        # Test the last page of kb24's tweets  <Wayne Shih> 25-Apr-2022
        response = self.anonymous_client.get(TWEET_LIST_URL, {
            'user_id': kb24.id,
            'created_at__lt': tweets[page_size * 2 - 1].created_at,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['has_next'], False)
        self.assertEqual(response.data['next'], None)
        self.assertEqual(len(response.data['tweets']), page_size)
        self.assertEqual(response.data['tweets'][0]['id'], tweets[page_size * 2].id)
        self.assertEqual(response.data['tweets'][page_size - 1]['id'], tweets[page_size * 3 - 1].id)

        # Test user1's new tweets  <Wayne Shih> 25-Apr-2022
        response = self.anonymous_client.get(TWEET_LIST_URL, {
            'user_id': kb24.id,
            'created_at__gt': tweets[0].created_at,
        })
        self.assertEqual(response.data['has_next'], False)
        self.assertEqual(response.data['next'], None)
        self.assertEqual(len(response.data['tweets']), 0)

        new_tweet1 = self.create_tweet(kb24, 'kb24::new_tweet::1')
        new_tweet2 = self.create_tweet(kb24, 'kb24::new_tweet::2')
        response = self.anonymous_client.get(TWEET_LIST_URL, {
            'user_id': kb24.id,
            'created_at__gt': tweets[0].created_at,
        })
        self.assertEqual(response.data['has_next'], False)
        self.assertEqual(response.data['next'], None)
        self.assertEqual(len(response.data['tweets']), 2)
        self.assertEqual(response.data['tweets'][0]['id'], new_tweet2.id)
        self.assertEqual(response.data['tweets'][1]['id'], new_tweet1.id)
