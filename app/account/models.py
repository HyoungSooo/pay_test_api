from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth.hashers import make_password, is_password_usable
from account.utils import validate_phone
from django.contrib.auth.base_user import BaseUserManager
import time

class UserManager(BaseUserManager):
    def create_user(self, phone_number, password, **extra_fields):

        if not phone_number:
            raise ValueError('휴대폰 번호를 입력해야합니다.')

        user = self.model(phone_number=phone_number ,**extra_fields)

        user.set_password(password)
        user.save(using=self._db)

        return user
    def create_superuser(self, phone_number, password, **extra_fields):        
       
        user = self.create_user(            
            phone_number = phone_number,                     
            password=password        
        )   

        user.is_staff = True
        user.is_superuser = True       
        user.save(using=self._db)     

        return 


class User(AbstractUser):
    username = models.CharField(blank=True, null=True, unique=False, max_length=10)
    phone_number = models.CharField(
        max_length=13, null=False, blank=False, unique=True, validators=[validate_phone])
    
    USERNAME_FIELD = 'phone_number'

    objects = UserManager()
    