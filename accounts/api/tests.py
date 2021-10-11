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
# $HISTORY$
# =================================================================================================


from rest_framework import status
from rest_framework.test import APIClient

from testing.testcases import TestCase


LOGIN_URL = '/api/accounts/login/'
LOGOUT_URL = '/api/accounts/logout/'
SIGNUP_URL = '/api/accounts/signup/'
LOGIN_STATUS_URL = '/api/accounts/login_status/'


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
        self.client = APIClient()
        self.user = self.create_user(
            username='fake_user',
            email='fake_user@twitter.com',
            password='correct_password',
        )

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
        self.assertEqual(response.data['user']['email'], 'fake_user@twitter.com')

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
        # print(response.data)
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
        # print(response.data)
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
        # print(response.data)
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
        # print(response.data)
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
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Please check input.')
        self.assertEqual(
            response.data['errors']['email'][0],
            'This email address has been occupied.'
        )

        # Test signup successfully  <Wayne Shih> 12-Aug-2021
        response = self.client.post(SIGNUP_URL, data)
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['user']['username'], 'someone')
        self.assertEqual(response.data['user']['email'], 'someone@fb.com')

        # Check now is at login state  <Wayne Shih> 12-Aug-2021
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['has_logged_in'], True)
