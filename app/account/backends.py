from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class PhoneNumberBackend(ModelBackend):
    def authenticate(self, request, **kwargs):
        UserModel = get_user_model()
        try:
            phone_number = kwargs.get('phone_number', None)
            user = UserModel.objects.get(phone_number=phone_number)
            if user.check_password(kwargs.get('password', None)):
              return user
        except UserModel.DoesNotExist:
            return None
        return None
