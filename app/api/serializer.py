from rest_framework import serializers
from rest_framework.settings import api_settings
from .models import Product, SIZE
from rest_framework import status
from core.utils import create_response_msg


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ("category", "name", "size", "cost",
                  "price", "des", "expiration_date", "barcode")

    barcode = serializers.ImageField(required=False)

    def create(self, validated_data):
        return Product.objects.create(**validated_data)


class ProductHandleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("category", "name", "size", "cost",
                  "price", "des", "expiration_date")

    category = serializers.CharField(required=False)
    name = serializers.CharField(required=False)
    size = serializers.ChoiceField(choices=SIZE, required=False)
    cost = serializers.IntegerField(required=False)
    price = serializers.IntegerField(required=False)
    des = serializers.CharField(required=False)
    expiration_date = serializers.DateTimeField(required=False)

    def update(self, instance, validated_data):
        instance.__dict__.update(**validated_data)

        for i in ['price', 'size', 'expiration_date', 'name']:
            if i in instance.__dict__:
                instance.save()
        instance.save(make_barcode=False)

        return instance
