from rest_framework import serializers
from django.contrib.auth import get_user_model
from account.models import Profile

UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    def create(self, validated_data):

        user = UserModel.objects.create_user(
            phone_number=validated_data['phone_number'],
            password=validated_data['password'],
        )

        return user

    class Meta:
        model = UserModel
        fields = ("id", "phone_number", "password", )


class UserLoginSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = UserModel
        fields = ("id", "phone_number", "password", )


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    nickname = serializers.CharField(required=False)

    class Meta:
        model = Profile
        fields = ('nickname', 'user')

    def create(self, validated_data):
        return Profile.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.__dict__.update(**validated_data)
        instance.save()
        return instance
