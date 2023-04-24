from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import CreateAPIView
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.hashers import check_password
from rest_framework.views import APIView
from core.utils import create_response_msg

from account.serializer import UserSerializer, UserLoginSerializer

from rest_framework_simplejwt.authentication import JWTAuthentication

class CreateUserView(CreateAPIView):

    model = get_user_model()
    permission_classes = [
        permissions.AllowAny 
    ]
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return create_response_msg(status.HTTP_201_CREATED, 'ok')

class UserLoginAPI(APIView):
    permission_classes = [
        permissions.AllowAny 
    ]
    serializer_class = UserLoginSerializer
    def post(self, request):
        phone_number = request.data.get('phone_number',None)
        password = request.data.get('password',None)

        user = get_user_model().objects.filter(phone_number=phone_number).first()

        if user is None:
            return create_response_msg(status.HTTP_400_BAD_REQUEST, '아이디/패스워드가 틀렸습니다.')

        if not check_password(password, user.password):
            return create_response_msg(status.HTTP_400_BAD_REQUEST, '아이디/패스워드가 틀렸습니다.')

      
        token = TokenObtainPairSerializer.get_token(user) 
        refresh_token = str(token) 
        access_token = str(token.access_token) 
        response = create_response_msg(status.HTTP_200_OK, 'ok', data = {'access_token' : access_token, 'refresh_token' : refresh_token})

        response.set_cookie("access_token", access_token, httponly=True)
        response.set_cookie("refresh_token", refresh_token, httponly=True)
        return response
        
class LogoutApi(APIView):
    permission_classes = [
        permissions.AllowAny 
    ]
    def get(self, request):
        """
        클라이언트 refreshtoken 쿠키를 삭제함으로 로그아웃처리
        """
        
        response = create_response_msg(status.HTTP_202_ACCEPTED, 'ok')
        response.delete_cookie('refresh_token')
        response.delete_cookie('access_token')

        return response
    

class TestApi(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    def post(self, request):
        return Response({'user':request.user.phone_number})