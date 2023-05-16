from django.core.management.base import BaseCommand, CommandError
from api.models import Product, Category
import json
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = '샘플 데이터베이스 생성'

    def handle(self, *args, **options):
          try:
            payload = {
              'phone_number': '010-1112-8657',
              'password': 'testpassword',
            }

            user = get_user_model().objects.create_user(
                **payload
            )

            with open('/usr/src/app/sample_data.json', 'r') as file:
                data = json.load(file)

            for payload in data:
                
                category = Category.objects.get_or_create(category = payload["category"])[0]

                payload.update({'category': category,'user' :user})
                Product.objects.create(**payload)

            self.stdout.write(self.style.SUCCESS(f'Successfully create sample data {Product.objects.count()}'))
          except:
              pass

        
        

