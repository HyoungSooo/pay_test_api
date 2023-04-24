from django.contrib import admin
from django.urls import path
from account.views import CreateUserView
from .views import UserLoginAPI, LogoutApi, TestApi

app_name = 'account'

urlpatterns = [
    path('test/', TestApi.as_view(), name='test'),
    path('api-jwt-auth/login/', UserLoginAPI.as_view(), name='login'),
    path('api-jwt-auth/logout/', LogoutApi.as_view(), name='logout'),
    path('api-jwt-auth/register/', CreateUserView.as_view(), name='register'),
]
