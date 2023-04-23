from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('account:register')
TOKEN_URL = reverse('account:login')
TEST_URL = reverse('account:test')


def create_user(**params):
    """Create a user and return new user"""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the users API (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful"""

        payload = {
            'phone_number': '010-1112-8654',
            'password': 'testpass',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(
            phone_number=payload['phone_number'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_phone_number_exists_error(self):
        """Test creating a user that already exists fails"""

        payload = {
            'phone_number': '010-1112-8654',
            'password': 'testpass',
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {
            'phone_number': '010-1112-8654',
            'password': 'testpass',
        }
        create_user(**payload)
        payload = {
            'phone_number': payload['phone_number'],
            'password': payload['password']
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('data', res.data)
        self.assertIn('access_token', res.data['data'])
        self.assertIn('refresh_token', res.data['data'])
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given"""
        create_user(phone_number='010-1234-7777', password='testpass')

        payload = {
            'phone_number': '010-1234-1234', 'password': 'badpass'}

        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test that token is not created if password is blank"""
        payload = {
            'phone_number': '010-1112-8654',
            'password': '',
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_access_token_is_worked(self):

        payload = {
            'phone_number': '010-1112-8657',
            'password': 'testpassword',
        }
        create_user(**payload)

        res = self.client.post(TOKEN_URL, payload)

        access_token = res.data['data'].get('access_token')

        self.client.credentials()

        res = self.client.post(
            TEST_URL, {}, HTTP_AUTHORIZATION=f' Bearer {access_token}')

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['user'], payload['phone_number'])

    def test_invaild_token_is_return_unathorize(self):

        payload = {
            'phone_number': '010-1112-8657',
            'password': 'testpassword',
        }
        create_user(**payload)

        res = self.client.post(TOKEN_URL, payload)

        access_token = res.data['data'].get(
            'access_token') + 'is_not_vaild'

        res = self.client.post(
            TEST_URL, {}, content_type="application/json", HTTP_AUTHORIZATION=f' Bearer {access_token}')

        self.assertEqual(res.status_code, 401)
