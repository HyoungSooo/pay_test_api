from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from django.contrib import admin
from django.urls import path
from account.views import CreateUserView
from .views import UserLoginAPI, LogoutApi, TestApi

app_name = 'account'

urlpatterns = [
    path('test/', TestApi.as_view(), name='test'),
    path('api-jwt-auth/login/', UserLoginAPI.as_view(), name='login'),
    path('api-jwt-auth/logout/', LogoutApi.as_view(), name='logout'),
    path('api-jwt-auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api-jwt-auth/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api-jwt-auth/register/', CreateUserView.as_view(), name='register'),
]
