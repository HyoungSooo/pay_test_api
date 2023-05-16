from django.db import models
import barcode
from io import BytesIO
from barcode.writer import ImageWriter
from django.core.files.base import File
from .utils import validate_date, korean_to_be_initial
import os
from django.contrib.auth import get_user_model


class Category(models.Model):
    category = models.CharField(max_length=20)

    def __str__(self) -> str:
        return self.category


class Product(models.Model):
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name='product')
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    price = models.IntegerField()
    name = models.CharField(max_length=20, unique=True)
    des = models.TextField()
    initial_set = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):

        self.initial_set = ''.join(korean_to_be_initial(self.name))
        return super().save(*args, **kwargs)
