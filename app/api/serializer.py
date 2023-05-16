from rest_framework import serializers
from .models import Product, Category


class ProductSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    category = serializers.CharField()

    class Meta:
        model = Product
        fields = ('price', 'des', 'name', 'category', 'user')

    def create(self, validated_data):
        category = validated_data.pop('category')
        category = Category.objects.get_or_create(category=category)[0]

        return Product.objects.create(category=category, **validated_data)


class ProductHandleSerializer(serializers.Serializer):
    category = serializers.CharField(required=False)
    name = serializers.CharField(required=False)
    price = serializers.IntegerField(required=False)
    des = serializers.CharField(required=False)

    def update(self, instance, validated_data):
        try:
            category = validated_data.pop('category')
            category = Category.objects.get_or_create(category=category)[0]
        except:
            category = instance.category.category

        instance.__dict__.update(**validated_data)
        instance.category = category
        instance.save()

        return instance
