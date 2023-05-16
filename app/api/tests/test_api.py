from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from api.utils import korean_to_be_initial

from django.db.models import Q
import datetime

from rest_framework.test import APIClient
from api.models import Product,Category
import os

TOKEN_URL = reverse('account:login')
PRODUCT_URL = reverse('api:product')
SEARCH_URL = reverse('api:product_search')

def product_patch_or_get_delete_url(product_id):
    """Return URL for product image upload"""
    return reverse('api:product_handle', kwargs = {'pk' : product_id})


def create_object(**payload):
    default = {
        'user': get_user_model().objects.first(),
        'category' : Category.objects.get_or_create(category = '음료')[0],
        'name' : '테스트음료',
        'price' : 10000,
        'des' : '테스트설명',
    }
    default.update(payload)

    return Product.objects.create(**default)

class ModelTest(TestCase):
    
    def test_korean_initial_is_maked(self):
        '''Test automatically creates a initial when instance is saved'''
        name_list = ['테스트', '테a스트', 'test임', 't테es스t트']

        payload = {
            'phone_number': '010-1112-8657',
            'password': 'testpassword',
        }

        user = get_user_model().objects.create_user(
            **payload
        )

        for name in name_list:
            payload = {
                'user' : user,
                'category' : Category.objects.get_or_create(category = '음료')[0],
                'name' : name
            }

            obj = create_object(**payload)

            self.assertTrue(obj.initial_set)
            self.assertEqual(''.join(korean_to_be_initial(name)), obj.initial_set)


class PublicUserApiTests(TestCase):
    """Test the users API (unauthenticated)"""
    maxDiff = 100000

    def setUp(self):
        self.client = APIClient()

    def test_auth_require_to_patch_or_get_url(self):
        '''Test unautenticated user will return 401'''
        res = self.client.get(product_patch_or_get_delete_url(1))

        self.assertEqual(res.status_code, 401)
        
        payload = {
            'name' : '조지아 크래프트 커피'
        }

        res = self.client.patch(product_patch_or_get_delete_url(1), payload)

        self.assertEqual(res.status_code, 401)


        res = self.client.delete(product_patch_or_get_delete_url(1))

        self.assertEqual(res.status_code, 401)

    
    def test_auth_require_to_create_view_list(self):
        res = self.client.get(PRODUCT_URL)
        
        self.assertEqual(res.status_code, 401)

        res = self.client.post(PRODUCT_URL, {})

        self.assertEqual(res.status_code, 401)

    
    def test_auth_require_search_api(self):
        res = self.client.get(SEARCH_URL + '?q=content')

        self.assertEqual(res.status_code, 401)
        

class PrivateProductApiTests(TestCase):
    """Test unauthenticated product API access"""

    maxDiff = None

    def setUp(self):
        '''Client setup, 
        force authentication function is not used.
        Instead, it stores the access token in the http header part.
        '''
        self.client = APIClient()
        payload = {
            'phone_number': '010-1112-8657',
            'password': 'testpassword',
        }
        self.user = get_user_model().objects.create_user(
            **payload
        )
        res = self.client.post(TOKEN_URL, payload)
        access_token = res.data['data'].get('access_token')

        self.client.defaults['HTTP_AUTHORIZATION'] = f' Bearer {access_token}'
    
    def test_get_product_detail(self):
        '''Test detail api is worked'''
        payload = {
            'user' : get_user_model().objects.first(),
            'name' : 'success',
        }
        content = create_object(**payload)

        res = self.client.get(product_patch_or_get_delete_url(content.id))

        self.assertEqual(res.status_code, 200)

        self.assertEqual(res.data['data'].get('name'), 'success')
        self.assertEqual(res.data['data'].get('category'), '음료')

    
    def test_patch_product(self):
        '''Test patch api is worked
        Implementation of the function to partially modify product properties.
        '''
        content = create_object()

        res = self.client.get(product_patch_or_get_delete_url(content.id))

        payload = {
            'user' : get_user_model().objects.first(),
            'category' : '과자',
            'name' : 'success',
        }
        
        patched_res = self.client.patch(product_patch_or_get_delete_url(content.id), data = payload)

        self.assertEqual(patched_res.status_code, 201)

        self.assertNotEqual(res.data['data'].get('name'), patched_res.data['data'].get('name'))
        self.assertNotEqual(res.data['data'].get('category'), patched_res.data['data'].get('category'))

    def test_delete_product(self):
        '''Test delete api is worked'''
        content = create_object()

        res = self.client.delete(product_patch_or_get_delete_url(content.id))

        self.assertEqual(res.status_code, 200)

        self.assertEqual(Product.objects.count(), 0)


    def test_create_product_api(self):
        '''Test create product data is worked'''

        payload = {
          'category' : '음료',
          'name' : '테스트',
          'price' : 10000,
          'des' : '테스트설명',
        }
        
        res = self.client.post(PRODUCT_URL, data = payload)

        self.assertEqual(res.status_code, 201)
        self.assertEqual(1, Product.objects.count())

        data = Product.objects.get(name = '테스트')

        for i in payload:
            if i == 'category':
                self.assertEqual(data.category.category, payload[i])
                continue
            self.assertEqual(data.__dict__[i], payload[i])

    def test_reject_when_insufficient_input_is_received_in_create_product_api(self):
        checklist = [
            {
              'name' : '테스트',
              'price' : 10000,
              'des' : '테스트설명',
            },
            {
              'name' : '테스트',
              'price' : 10000,
            },
            {
              'price' : 10000,
            },
        ]

        for check in checklist:
            res = self.client.post(PRODUCT_URL, data = check)

            self.assertEqual(res.status_code, 400)
            self.assertEqual(0, Product.objects.count())

    def test_cursor_pagination_api(self):
        per = 10

        for i in range(97, 118):
            payload = {
                'name' : chr(i)
            }   

            create_object(**payload)

        self.assertEqual(21, Product.objects.count())

        first_res = self.client.get(PRODUCT_URL)

        self.assertEqual(first_res.status_code, 200)

        self.assertIn('next', first_res.data['data'])
        self.assertTrue(first_res.data['data']['next'])
        self.assertIn('previous', first_res.data['data'])
        self.assertFalse(first_res.data['data']['previous'])
        self.assertIn('results', first_res.data['data'])
        self.assertEqual(per, len(first_res.data['data']['results']))

        second_res = self.client.get(first_res.data['data']['next'])

        self.assertNotEqual(second_res.data['data']['results'], first_res.data['data']['results'])

        self.assertTrue(second_res.data['data']['next'])
        self.assertTrue(second_res.data['data']['previous'])
        self.assertEqual(per, len(second_res.data['data']['results']))

        last_res = self.client.get(second_res.data['data']['next'])

        self.assertNotEqual(second_res.data['data']['results'], last_res.data['data']['results'])
        
        self.assertFalse(last_res.data['data']['next'])
        self.assertTrue(last_res.data['data']['previous'])
        self.assertEqual(1, len(last_res.data['data']['results']))



    def test_search_api(self):
        """Test search api is work (full text, initial text)"""

        search_list = ['슈크림 라떼', '슈크힘 라떼', '슈흐림 라떼', '휴크림 라떼', '슈크함 라떼']

        for name in search_list:
            payload = {
                'name' : name
            }

            create_object(**payload)

        
        res = self.client.get(SEARCH_URL + '?q=라떼')

        self.assertEqual(res.status_code, 200)

        self.assertEqual(len(res.data.get('data')), 5)

        res = self.client.get(SEARCH_URL + '?q=ㄹㄸ')

        self.assertEqual(len(res.data.get('data')), 5)
        
        res = self.client.get(SEARCH_URL + '?q=슈크림')

        self.assertEqual(len(res.data.get('data')), 1)
        
        res = self.client.get(SEARCH_URL + '?q=ㅅㅋ')

        self.assertEqual(len(res.data.get('data')), 3)
        
        res = self.client.get(SEARCH_URL + '?q=크림')

        self.assertEqual(len(res.data.get('data')), 2)

    def test_search_api_can_return_no_content(self):
        
        search_list = ['슈크림 라떼', '슈크힘 라떼', '슈흐림 라떼', '휴크림 라떼', '슈크함 라떼']

        for name in search_list:
            payload = {
                'name' : name
            }

            create_object(**payload)

        res = self.client.get(SEARCH_URL + '?q=컨텐츠가없어요')

        self.assertEqual(res.status_code, 204)

    def test_other_user_cant_handle_own_product(self):
        content = create_object()

        payload = {
            'phone_number': '010-1234-1234',
            'password': 'test123'
        }
        user = get_user_model().objects.create_user(
          **payload
        )

        other_client = APIClient()


        res = other_client.post(TOKEN_URL, payload)
        access_token = res.data['data'].get('access_token')

        other_client.defaults['HTTP_AUTHORIZATION'] = f' Bearer {access_token}'

        
        delete_res = other_client.delete(product_patch_or_get_delete_url(content.id))

        self.assertEqual(delete_res.status_code, 401)

        patch_res = other_client.patch(product_patch_or_get_delete_url(content.id), {'name':'test'})

        self.assertEqual(patch_res.status_code, 401)
