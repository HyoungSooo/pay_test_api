from rest_framework import serializers
from .models import Product, Category, Review


class ProductSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.nickname')
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


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.nickname', read_only=True)
    product = serializers.CharField(source='product.username', read_only=True)
    created_at = serializers.DateTimeField(
        required=False, source='review.created_at', read_only=True)

    class Meta:
        model = Review
        fields = ('product', 'user', 'rating',
                  'title', 'content', 'created_at')

    class ReviewGETSerializer(serializers.ModelSerializer):
        class Meta:
            model = Review
            fields = '__all__'
