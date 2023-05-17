from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import CreateAPIView
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.hashers import check_password
from rest_framework.views import APIView
from core.utils import create_response_msg
from account.serializer import UserSerializer, UserLoginSerializer,ProfileSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes


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
    
class ProfileCreateApi(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    authentication_classes = (JWTAuthentication,)
    serializer_class = ProfileSerializer

    def get_queryset(self, pk):
        try:
            return get_user_model().objects.get(pk = pk).profile
        except:
            return False
        
    def post(self, request):
        
        profile = self.get_queryset(request.user.id)

        if profile:
            return create_response_msg(status.HTTP_400_BAD_REQUEST, 'profile is already created')
        
        serializer = ProfileSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)

            return create_response_msg(status.HTTP_201_CREATED, 'profile create success', serializer.data)

        return create_response_msg(status.HTTP_400_BAD_REQUEST, 'serialize error', data=request.data)
    
class UserProfileAPI(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    authentication_classes = (JWTAuthentication,)
    serializer_class = ProfileSerializer

    def get_queryset(self, pk):
        try:
            return get_user_model().objects.get(id= pk).profile
        except:
            return False
    
    
    def get(self,request):
        data = self.get_queryset(request.user.id)

        if not data:
            return create_response_msg(status.HTTP_400_BAD_REQUEST, 'create profile first')
        
        serializer = ProfileSerializer(data)
        data = {'kindness': request.user.profile.kindness}
        data.update(serializer.data)
        data['user'] = request.user.id
        
        return create_response_msg(status.HTTP_200_OK, 'ok', data)
    def patch(self, request):
        profile = self.get_queryset(request.user.id)

        if not profile:
            return create_response_msg(status.HTTP_400_BAD_REQUEST, 'no profile')
        
        serializer = ProfileSerializer(profile, data = request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
            serializer.data['kindness'] = request.user.profile.kindness
            return create_response_msg(status.HTTP_200_OK, 'ok', data=serializer.data)

        return create_response_msg(status.HTTP_400_BAD_REQUEST, 'serialize error', data=request.data)
    @extend_schema(parameters=[OpenApiParameter(name='method', description='method, plus or minus',
                                                required=True, type=str)])
    def post(self, request):
        profile = self.get_queryset(request.user.id)

        if not profile:
            return create_response_msg(status.HTTP_400_BAD_REQUEST, 'no profile')
        
        method = request.query_params.get('method', None)
        
        if method == 'plus':
            profile.plus_kindness()
            return create_response_msg(status.HTTP_202_ACCEPTED, 'ok', data = {'kindness' : profile.kindness, 'user' : profile.user.id})
        elif method == 'minus':
            profile.minus_kindness()
            return create_response_msg(status.HTTP_202_ACCEPTED, 'ok', data = {'kindness' : profile.kindness, 'user' : profile.user.id})
        else:
            return create_response_msg(status.HTTP_400_BAD_REQUEST, 'please write the method in query params user method=<plus or minus>')



class TestApi(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    def post(self, request):
        return Response({'user':request.user.phone_number})