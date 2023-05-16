from django.db import models
from django.contrib.auth.models import AbstractUser
from account.utils import validate_phone
from django.contrib.auth.base_user import BaseUserManager

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

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=20)
    kindness = models.IntegerField(null=True,blank=True, default= 100)

    def plus_kindness(self):
        self.kindness += 1
        self.save()
        return self.kindness
    
    def minus_kindness(self):
        self.kindness -= 2
        self.save()
        return self.kindness
    
    def __str__(self) -> str:
        return self.nickname
    
        