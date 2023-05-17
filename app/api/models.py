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
    name = models.CharField(max_length=20)
    des = models.TextField()
    initial_set = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):

        self.initial_set = ''.join(korean_to_be_initial(self.name))
        return super().save(*args, **kwargs)


class Review(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.product.name} by {self.user.username}"
