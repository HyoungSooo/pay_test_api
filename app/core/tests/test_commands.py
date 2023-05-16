from django.test import TransactionTestCase
from django.core.management import call_command
from api.models import Product, Category
from django.contrib.auth import get_user_model

class CommandsTest(TransactionTestCase):
    def test_change_database_setting_command(self):
        
        call_command('change_database_charactor_set')
        payload = {
            'phone_number': '010-1112-8657',
            'password': 'testpassword',
        }

        user = get_user_model().objects.create_user(
            **payload
        )
        
        payload = {
          "user":user,
          "category" : "음료",
          "name" : "슈크림 라떼",
          "price" : 10000,
          "des" : "달달한 슈크림 라떼"
        }

        category = Category.objects.get_or_create(category = payload["category"])[0]

        payload.update({'category': category})

        content = Product.objects.create(**payload)

        self.assertTrue(content)

    
    def test_create_sample_data_command(self):
        
        call_command('create_sample_data')

        self.assertEqual(Product.objects.count(), 17)
        

        