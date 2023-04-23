from django.db import models
import barcode
from io import BytesIO
from barcode.writer import ImageWriter
from django.core.files.base import File
from .utils import validate_date, korean_to_be_initial
import os

SIZE = (
    ('L', 'Large'),
    ('S', 'Small')
)


class Product(models.Model):
    category = models.CharField(max_length=30)
    price = models.IntegerField()
    cost = models.IntegerField()
    name = models.CharField(max_length=20, unique=True)
    des = models.TextField()
    barcode = models.ImageField(upload_to='images/', blank=True)
    expiration_date = models.DateTimeField(validators=[validate_date])
    size = models.CharField(max_length=1, choices=SIZE)
    initial_set = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return str(self.name)

    def save(self, make_barcode=True, *args, **kwargs):

        self.initial_set = ''.join(korean_to_be_initial(self.name))

        if make_barcode:

            korea_unicode = '-'.join([str(ord(i)) for i in self.name])
            code = barcode.get_barcode_class('code128')
            ean = code(f'{self.price}{self.expiration_date}{self.id}{korea_unicode}{self.size}',
                       writer=ImageWriter())
            buffer = BytesIO()
            ean.write(buffer)
            title = self.name.replace(' ', '')
            if os.path.isfile(f'/usr/src/app/images/{title}.png'):
                os.remove(f'/usr/src/app/images/{title}.png')
            self.barcode.save(f'{title}.png', File(buffer), save=False)
        return super().save(*args, **kwargs)
