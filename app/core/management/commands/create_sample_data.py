from django.core.management.base import BaseCommand, CommandError
from api.models import Product
import json

class Command(BaseCommand):
    help = '샘플 데이터베이스 생성'

    def handle(self, *args, **options):
        try:
          with open('/usr/src/app/sample_data.json', 'r') as file:
              data = json.load(file)

          for payload in data:
              Product.objects.create(**payload)

          self.stdout.write(self.style.SUCCESS(f'Successfully create sample data {Product.objects.count()}'))
        except :
            self.stdout.write(self.style.SUCCESS('call for once'))
            

        
        

