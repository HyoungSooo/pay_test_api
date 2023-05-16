from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from account.models import User, Profile

CREATE_USER_URL = reverse('account:register')
TOKEN_URL = reverse('account:login')
TEST_URL = reverse('account:test')
PROFILE_URL = reverse('account:profile')


def user_profile():
    return reverse('account:user_profile')


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

    def test_create_profile(self):
        profile_payload = {
            'nickname': 'test'
        }

        payload = {
            'phone_number': '010-1112-8657',
            'password': 'testpassword',
        }
        create_user(**payload)

        token_res = self.client.post(TOKEN_URL, payload)

        access_token = token_res.data['data'].get(
            'access_token')

        res = self.client.post(
            PROFILE_URL, profile_payload, HTTP_AUTHORIZATION=f' Bearer {access_token}')

        self.assertEqual(res.status_code, 201)

        profile = Profile.objects.select_related('user').get(id=1)

        self.assertEqual(profile.nickname, profile_payload['nickname'])
        self.assertEqual(profile.user.phone_number, payload['phone_number'])

    def test_user_profile_detail(self):

        profile_payload = {
            'nickname': 'test'
        }

        payload = {
            'phone_number': '010-1112-8657',
            'password': 'testpassword',
        }
        create_user(**payload)

        token_res = self.client.post(TOKEN_URL, payload)

        access_token = token_res.data['data'].get(
            'access_token')

        self.client.post(
            PROFILE_URL, profile_payload, HTTP_AUTHORIZATION=f' Bearer {access_token}')

        res = self.client.get(user_profile(),
                              HTTP_AUTHORIZATION=f' Bearer {access_token}')

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data.get('data').get(
            'nickname'), profile_payload['nickname'])

    def test_user_create_profile_more_than_once(self):
        profile_payload = {
            'nickname': 'test'
        }

        payload = {
            'phone_number': '010-1112-8657',
            'password': 'testpassword',
        }
        user = create_user(**payload)

        token_res = self.client.post(TOKEN_URL, payload)

        access_token = token_res.data['data'].get(
            'access_token')

        self.client.post(
            PROFILE_URL, profile_payload, HTTP_AUTHORIZATION=f' Bearer {access_token}')

        res = self.client.post(
            PROFILE_URL, profile_payload, HTTP_AUTHORIZATION=f' Bearer {access_token}')

        self.assertEqual(res.status_code, 400)

    def test_patch_profile(self):
        profile_payload = {
            'nickname': 'test'
        }

        payload = {
            'phone_number': '010-1112-8657',
            'password': 'testpassword',
        }
        patch_payload = {
            'nickname': 'test_nickname'
        }
        create_user(**payload)

        token_res = self.client.post(TOKEN_URL, payload)

        access_token = token_res.data['data'].get(
            'access_token')

        self.client.post(
            PROFILE_URL, profile_payload, HTTP_AUTHORIZATION=f' Bearer {access_token}')

        res = self.client.patch(
            user_profile(), patch_payload, HTTP_AUTHORIZATION=f' Bearer {access_token}')

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data.get('data').get(
            'nickname'), patch_payload['nickname'])

    def test_user_profile_plus_or_minus_kindness(self):
        profile_payload = {
            'nickname': 'test'
        }

        payload = {
            'phone_number': '010-1112-8657',
            'password': 'testpassword',
        }
        patch_payload = {
            'nickname': 'test_nickname'
        }
        user = create_user(**payload)

        token_res = self.client.post(TOKEN_URL, payload)

        access_token = token_res.data['data'].get(
            'access_token')

        self.client.post(
            PROFILE_URL, profile_payload, HTTP_AUTHORIZATION=f' Bearer {access_token}')

        res = self.client.post(
            user_profile() + '?method=plus', HTTP_AUTHORIZATION=f' Bearer {access_token}')

        self.assertEqual(res.status_code, 202)
        self.assertEqual(res.data.get('data').get('kindness'), 101)

        self.assertEqual(user.profile_set.first().kindness, 101)

        res = self.client.post(
            user_profile() + '?method=minus', HTTP_AUTHORIZATION=f' Bearer {access_token}')

        self.assertEqual(res.status_code, 202)
        self.assertEqual(res.data.get('data').get('kindness'), 99)

        self.assertEqual(user.profile_set.first().kindness, 99)

        res = self.client.post(
            user_profile() + '?method=unvalid', HTTP_AUTHORIZATION=f' Bearer {access_token}')

        self.assertEqual(res.status_code, 400)
