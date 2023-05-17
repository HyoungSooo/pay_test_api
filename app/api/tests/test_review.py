from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from api.models import Product, Review
from django.contrib.auth import get_user_model
from .test_api import TOKEN_URL, create_object
from django.urls import reverse


def review_list(pk):
    return reverse('api:review-list', kwargs={'product_id': pk})


def review_detail(pk):
    return reverse('api:review-detail', kwargs={'pk': pk})


def create_review(**payload):
    default = {
        'user': get_user_model().objects.first(),
        'product': create_object(),
        'title': 'test',
        'content': 'test',
        'rating': 5
    }

    default.update(payload)

    return Review.objects.create(**default)


class ReviewAPITestCase(TestCase):
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
        self.product = create_object()
        res = self.client.post(TOKEN_URL, payload)
        access_token = res.data['data'].get('access_token')

        self.client.defaults['HTTP_AUTHORIZATION'] = f' Bearer {access_token}'

        self.other_user = get_user_model().objects.create_user(
            **{
                'phone_number': '010-1234-1344',
                'password': 'testtest'
            }
        )

    def test_get_reviews_list(self):
        create_review(**{'product': self.product})
        res = self.client.get(review_list(self.product.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data.get('data')), 1)

    def test_create_review(self):
        data = {
            'title': 'Test Review',
            'content': 'This is a test review.',
            'rating': 4
        }
        res = self.client.post(
            review_list(self.product.id), data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_get_review_detail(self):
        review = create_review()
        res = self.client.get(review_detail(review.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get('data').get('title'), 'test')
        self.assertEqual(res.data.get('data').get('content'), 'test')
        self.assertEqual(res.data.get('data').get('rating'), 5)

    def test_update_review(self):
        review = Review.objects.create(product=self.product, user=self.user,
                                       title='Test Review', content='This is a test review.', rating=4)
        data = {
            'title': 'Updated Review',
            'rating': 5
        }
        res = self.client.patch(
            review_detail(review.id), data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get('data')['title'], 'Updated Review')
        self.assertEqual(res.data.get('data')['rating'], 5)

        other_review = Review.objects.create(product=self.product, user=self.other_user,
                                             title='Test Review', content='This is a test review.', rating=4)

        res = self.client.patch(
            review_detail(other_review.id), data)

        self.assertEqual(res.status_code, 401)

    def test_delete_review(self):
        review = Review.objects.create(product=self.product, user=self.user,
                                       title='Test Review', content='This is a test review.', rating=4)
        response = self.client.delete(review_detail(review.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.filter(pk=review.id).exists())

        other_review = Review.objects.create(product=self.product, user=self.other_user,
                                             title='Test Review', content='This is a test review.', rating=4)
        res = self.client.patch(
            review_detail(other_review.id))

        self.assertEqual(res.status_code, 401)
        self.assertTrue(Review.objects.filter(pk=other_review.id).exists())
