from django.contrib import admin
from django.urls import path, include
from account.views import CreateUserView
from .views import UserLoginAPI, LogoutApi, TestApi, ProfileApi, UserAPI
from rest_framework_simplejwt.views import TokenRefreshView


app_name = 'account'

urlpatterns = [
    path('test/', TestApi.as_view(), name='test'),
    path('login/', UserLoginAPI.as_view(), name='login'),
    path('logout/', LogoutApi.as_view(), name='logout'),
    path('register/', CreateUserView.as_view(), name='register'),
    path('refresh/', TokenRefreshView.as_view()),
    path('profile/', ProfileApi.as_view(), name='profile'),
    path('user/', UserAPI.as_view(), name='user_profile')
]
