from django.test import TransactionTestCase
from django.core.management import call_command
from api.models import Product
import os
import json

class CommandsTest(TransactionTestCase):
    def test_change_database_setting_command(self):
        
        call_command('change_database_charactor_set')

        payload = {
          "category" : "음료",
          "name" : "슈크림 라떼",
          "price" : 10000,
          "cost" : 5000,
          "des" : "달달한 슈크림 라떼",
          "size" : "S",
          "expiration_date": "2023-04-30T13:26:47+09:00"
        }

        content = Product.objects.create(**payload)

        self.assertTrue(content)

        os.remove(f'/usr/src/app/images/{payload["name"].replace(" ", "")}.png')

    
    def test_create_sample_data_command(self):
        
        call_command('create_sample_data')

        self.assertEqual(Product.objects.count(), 17)

        with open('/usr/src/app/sample_data.json', 'r') as file:
              data = json.load(file)

        for payload in data:
              os.remove(f'/usr/src/app/images/{payload["name"].replace(" ", "")}.png')

        

        