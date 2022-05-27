# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#           account api unit tests
#
# =================================================================================================
#    Date      Name                    Description of Change
# 12-Aug-2021  Wayne Shih              Initial create
# 07-Sep-2021  Wayne Shih              React to refactoring TestCase
# 10-Oct-2021  Wayne Shih              React to pylint checks
# 27-Feb-2022  Wayne Shih              Add a test for DRF API list page and tests for login
# 20-Mar-2022  Wayne Shih              Add a test for UserProfile model
# 23-Mar-2022  Wayne Shih              Add tests for UserProfile & User APIs, react to serializer change
# 26-May-2022  Wayne Shih              Add clear cache before each test
# $HISTORY$
# =================================================================================================


from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import UserProfile
from testing.testcases import TestCase


ACCOUNTS_BASE_URL = '/api/accounts/'
LOGIN_URL = '/api/accounts/login/'
LOGOUT_URL = '/api/accounts/logout/'
SIGNUP_URL = '/api/accounts/signup/'
LOGIN_STATUS_URL = '/api/accounts/login_status/'
USER_PROFILES_BASE_URL = '/api/profiles/'
USER_PROFILES_DETAIL_URL = '/api/profiles/{}/'
USER_BASE_URL = '/api/users/'
USER_DETAIL_URL = '/api/users/{}/'


# <Wayne Shih> 12-Aug-2021
# - tests.py could be under any directory in fact.
#   as long as the test class is inherited from TestCase.
# - Need to start with "test_" to name all unit tests as a method in the case.
# - Each "test_" method is a unit test, which could include multiple cases
#   in order to be efficient.
# - Note: Django's unit tests take around 1 hour, which is relatively slow.
# - Use
#     $ python manage.py test
#   or
#     $ python manage.py test -v2
#   to run tests.
# - It creates a test database, e.g. 'test_twitter', everytime we run the test
#   so that it will not mess up the original database 'twitter'.
class AccountApiTests(TestCase):

    # <Wayne Shih> 12-Aug-2021
    # This method will be executed before executing each test method
    def setUp(self):
        self.clear_cache()
        self.client = APIClient()
        self.user = self.create_user(
            username='fake_user',
            email='fake_user@twitter.com',
            password='correct_password',
        )

    def test_drf_api_list_page(self):
        response = self.anonymous_client.get(ACCOUNTS_BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # <Wayne Shih> 12-Aug-2021
    # The name of each test method must start with 'test_'.
    def test_login(self):
        # <Wayne Shih> 12-Aug-2021
        # Test if use GET, expect http status code to be 405 = METHOD_NOT_ALLOWED.
        response = self.client.get(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct_password',
        })
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.data['detail'], 'Method "GET" not allowed.')

        # Test wrong password  <Wayne Shih> 12-Aug-2021
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'wrong_password',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Username and password do not match.')

        # Test non exist user  <Wayne Shih> 12-Aug-2021
        response = self.client.post(LOGIN_URL, {
            'username': 'non_exist_user',
            'password': 'any_password',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'User does not exit.')

        # Test missing password  <Wayne Shih> 12-Aug-2021
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')
        self.assertEqual(
            response.data['errors'],
            'Request is missing param(s): password. All missing params are required to provide.'
        )

        # Test blank username and password  <Wayne Shih> 27-Feb-2022
        response = self.client.post(LOGIN_URL, {
            'username': '',
            'password': '',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')
        self.assertEqual(
            response.data['errors']['username'][0],
            'This field may not be blank.'
        )
        self.assertEqual(
            response.data['errors']['password'][0],
            'This field may not be blank.'
        )

        # Check now is at not login state  <Wayne Shih> 12-Aug-2021
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['has_logged_in'], False)

        # Test login successfully  <Wayne Shih> 12-Aug-2021
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct_password',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data['user'], None)
        self.assertEqual(response.data['user']['id'], self.user.id)

        # Check now is at login state  <Wayne Shih> 12-Aug-2021
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['has_logged_in'], True)

    def test_logout(self):
        self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct_password',
        })

        # Check now is at login state  <Wayne Shih> 12-Aug-2021
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

        # Test if use GET to logout  <Wayne Shih> 12-Aug-2021
        response = self.client.get(LOGOUT_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Test if use POST to logout successfully  <Wayne Shih> 12-Aug-2021
        response = self.client.post(LOGOUT_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], True)

        # Check now is at not login state  <Wayne Shih> 12-Aug-2021
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['has_logged_in'], False)

    def test_signup(self):
        data = {
            'username': 'someone',
            'email': 'someone@fb.com',
            'password': 'any_password',
        }

        # Test if use GET to signup  <Wayne Shih> 12-Aug-2021
        response = self.client.get(SIGNUP_URL, data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Test wrong email format  <Wayne Shih> 12-Aug-2021
        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'email': 'not a correct email',
            'password': 'any_password'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')
        self.assertEqual(response.data['errors']['email'][0], 'Enter a valid email address.')

        # Test if password is too short (< 6)  <Wayne Shih> 12-Aug-2021
        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'email': 'someone@fb.com',
            'password': '123',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')
        self.assertEqual(
            response.data['errors']['password'][0],
            'Ensure this field has at least 6 characters.'
        )

        # Test if username is too long (> 20)  <Wayne Shih> 12-Aug-2021
        response = self.client.post(SIGNUP_URL, {
            'username': 'username_is_tooooooooooooooooo_loooooooong',
            'email': 'someone@google.com',
            'password': 'any_password',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')
        self.assertEqual(
            response.data['errors']['username'][0],
            'Ensure this field has no more than 20 characters.'
        )

        # Test if username has been occupied  <Wayne Shih> 21-Aug-2021
        response = self.client.post(SIGNUP_URL, {
            'username': self.user.username,
            'email': 'someone@google.com',
            'password': 'any_password',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')
        self.assertEqual(
            response.data['errors']['username'][0],
            'This username has been occupied.'
        )

        # Test if email has been occupied  <Wayne Shih> 21-Aug-2021
        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'email': self.user.email,
            'password': 'any_password',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')
        self.assertEqual(
            response.data['errors']['email'][0],
            'This email address has been occupied.'
        )

        # Test signup successfully  <Wayne Shih> 12-Aug-2021
        response = self.client.post(SIGNUP_URL, data)
        user = User.objects.filter(username=response.data['user']['username']).first()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['user']['username'], user.username)
        self.assertEqual(response.data['user']['id'], user.id)
        self.assertEqual(UserProfile.objects.filter(user_id=user.id).exists(), True)

        # Check now is at login state  <Wayne Shih> 12-Aug-2021
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['has_logged_in'], True)


class UserApiTests(TestCase):

    def setUp(self):
        self.mj23, self.mj23_client = self.create_user_and_auth_client(username='mj23')
        self.mj23.is_superuser = True
        self.lbj23, self.lbj23_client = self.create_user_and_auth_client(username='lbj23')
        self.lbj23.is_staff = True
        self.kd35, self.kd35_client = self.create_user_and_auth_client(username='kd35')
        self.kd35_client.put(USER_PROFILES_DETAIL_URL.format(self.kd35.profile.id), {
            'nickname': 'kd35',
            'avatar': SimpleUploadedFile(
                name='cupcake-photo.jpg',
                content=str.encode('cupcake image'),
                content_type='image/jpeg',
            ),
        })

    def test_list_api(self):
        # Non-login user  <Wayne Shih> 23-Mar-2022
        response = self.anonymous_client.get(USER_BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data['detail'],
            'Authentication credentials were not provided.'
        )

        # Regular login user  <Wayne Shih> 23-Mar-2022
        response = self.kd35_client.get(USER_BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data['detail'],
            'You do not have permission to perform this action.'
        )

        # Staff user  <Wayne Shih> 23-Mar-2022
        response = self.lbj23_client.get(USER_BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data['detail'],
            'You do not have permission to perform this action.'
        )

        # Super user can't create user  <Wayne Shih> 23-Mar-2022
        response = self.mj23_client.post(USER_BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Super user  <Wayne Shih> 23-Mar-2022
        response = self.mj23_client.get(USER_BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

    def test_retrieve_api(self):
        url = USER_DETAIL_URL.format(self.lbj23.id)

        # Super user  <Wayne Shih> 23-Mar-2022
        response = self.mj23_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.json().keys()), {'id', 'username', 'nickname', 'avatar_url'})
        self.assertEqual(response.data['id'], self.lbj23.id)
        self.assertEqual(response.data['username'], self.lbj23.username)

        # Super user can't modify user  <Wayne Shih> 23-Mar-2022
        response = self.mj23_client.put(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.mj23_client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Staff user  <Wayne Shih> 23-Mar-2022
        response = self.lbj23_client.get(url)
        self.assertEqual(
            response.data['detail'],
            'You do not have permission to perform this action.'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Regular login user  <Wayne Shih> 23-Mar-2022
        response = self.kd35_client.get(url)
        self.assertEqual(
            response.data['detail'],
            'You do not have permission to perform this action.'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Non-login user  <Wayne Shih> 23-Mar-2022
        response = self.anonymous_client.get(url)
        self.assertEqual(
            response.data['detail'],
            'Authentication credentials were not provided.'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_api(self):
        url = USER_DETAIL_URL.format(self.lbj23.id)

        # Non-login user  <Wayne Shih> 23-Mar-2022
        response = self.anonymous_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data['detail'],
            'Authentication credentials were not provided.'
        )

        # Regular login user  <Wayne Shih> 23-Mar-2022
        response = self.kd35_client.delete(url)
        self.assertEqual(
            response.data['detail'],
            'You do not have permission to perform this action.'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Staff user  <Wayne Shih> 23-Mar-2022
        response = self.lbj23_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data['detail'],
            'You do not have permission to perform this action.'
        )

        # Super user  <Wayne Shih> 23-Mar-2022
        response = self.mj23_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 2)


class UserProfileApiTests(TestCase):

    def setUp(self):
        self.lbj23, self.lbj23_client = self.create_user_and_auth_client(username='lbj23')
        self.lbj23_profile = self.lbj23.profile
        self.lbj23.profile.nickname = 'old nickname'
        self.lbj23.profile.save()
        self.kd35, self.kd35_client = self.create_user_and_auth_client(username='kd35')

    def test_drf_api_list_page(self):
        response = self.anonymous_client.get(USER_PROFILES_BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_api(self):
        url = USER_PROFILES_DETAIL_URL.format(self.lbj23.profile.id)

        # Non-login users  <Wayne Shih> 23-Mar-2022
        response = self.anonymous_client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.anonymous_client.put(url, {'nickname': 'new nickname'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data['detail'],
            'Authentication credentials were not provided.'
        )

        # kd35 is not the profile owner  <Wayne Shih> 23-Mar-2022
        response = self.kd35_client.get(url, {'nickname': 'new nickname'})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.kd35_client.put(url, {'nickname': 'new nickname'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data['detail'],
            'You do not have permission to access this object.'
        )

        # Missing param  <Wayne Shih> 23-Mar-2022
        response = self.kd35_client.put(url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')
        self.assertEqual(
            response.data['errors'],
            'Request is missing param(s): nickname/avatar. '
            'At least one missing param is required to provide.'
        )

        # lbj23 update an invalid nickname  <Wayne Shih> 23-Mar-2022
        invalid_nickname = '1' * 200
        response = self.lbj23_client.put(url, {'nickname': invalid_nickname})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')
        self.assertEqual(
            response.data['errors']['nickname'][0],
            'Ensure this field has no more than 100 characters.'
        )

        # lbj23 update an invalid avatar  <Wayne Shih> 23-Mar-2022
        response = self.lbj23_client.put(url, {'avatar': 'invalid avatar'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')
        self.assertEqual(
            response.data['errors']['avatar'][0],
            'The submitted data was not a file. Check the encoding type on the form.'
        )

        # lbj23 update his nickname  <Wayne Shih> 23-Mar-2022
        response = self.lbj23_client.put(url, {'nickname': 'new nickname'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nickname'], 'new nickname')
        self.assertEqual(response.data['avatar'], self.lbj23.profile.avatar)

        # lbj23 update his avatar  <Wayne Shih> 23-Mar-2022
        self.lbj23.profile.refresh_from_db()
        response = self.lbj23_client.put(url, {
            'avatar': SimpleUploadedFile(
                name='lbj-avatar.jpg',
                content=str.encode('a fake image'),
                content_type='image/jpeg',
            ),
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nickname'], self.lbj23.profile.nickname)
        self.assertEqual('lbj-avatar' in response.data['avatar'], True)

        # lbj23 update his nickname & avatar  <Wayne Shih> 23-Mar-2022
        self.lbj23.profile.refresh_from_db()
        response = self.lbj23_client.put(url, {
            'nickname': 'king lbj',
            'avatar': SimpleUploadedFile(
                name='king-lbj-photo.jpg',
                content=str.encode('GOAT image'),
                content_type='image/jpeg',
            ),
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nickname'], 'king lbj')
        self.assertEqual('king-lbj-photo' in response.data['avatar'], True)
