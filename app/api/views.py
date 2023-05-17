from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework import status
from core.utils import create_response_msg
from .models import Product, Review
from .serializer import ProductHandleSerializer, ProductSerializer, ReviewSerializer
from django.db.models import Q
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from rest_framework.pagination import CursorPagination
from drf_yasg.utils import swagger_auto_schema


class ProductCursorPagination(CursorPagination):
    page_size = 10
    ordering = 'id'


class ProductApiView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ProductCursorPagination
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.all()

    def get(self, request):
        queryset = self.get_queryset()
        paginator = self.pagination_class()
        results = paginator.paginate_queryset(queryset, request)
        serializer = ProductSerializer(results, many=True)
        data = paginator.get_paginated_response(
            serializer.data).__dict__['data']
        return create_response_msg(status.HTTP_200_OK, 'cursor based list view', data=data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)

            return create_response_msg(status.HTTP_201_CREATED, 'objects create success', serializer.data)

        return create_response_msg(status.HTTP_400_BAD_REQUEST, 'serialize error', data=request.data)


class ProductHandleApiView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProductHandleSerializer

    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except:
            return False

    def get(self, request, pk):
        content = self.get_object(pk)
        if not content:
            return create_response_msg(status.HTTP_204_NO_CONTENT, 'no content')
        serializer = ProductHandleSerializer(content)

        return create_response_msg(status.HTTP_200_OK, 'ok', data=serializer.data)

    def patch(self, request, pk):
        content = self.get_object(pk)

        if request.user != content.user:
            return create_response_msg(status.HTTP_401_UNAUTHORIZED, 'unauthorize')

        if not content:
            return create_response_msg(status.HTTP_204_NO_CONTENT, 'no content')

        serializer = ProductHandleSerializer(content, data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return create_response_msg(status.HTTP_201_CREATED, 'ok', data=serializer.data)

        return create_response_msg(status.HTTP_400_BAD_REQUEST, 'serialize error', data=request.data)

    def delete(self, request, pk):
        content = Product.objects.get(pk=pk)

        if request.user != content.user:
            return create_response_msg(status.HTTP_401_UNAUTHORIZED, 'unauthorize')

        content.delete()

        return create_response_msg(status.HTTP_200_OK, 'ok')


class ProductSearchView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self, condition: Q = None):
        if not condition:
            condition = Q()

        return Product.objects.filter(condition)

    @extend_schema(parameters=[OpenApiParameter(name='q', description='query product title',
                                                required=True, type=str)])
    def get(self, request):
        string = request.query_params.get('q', None)
        if string:
            q = Q()
            q |= Q(name__icontains=string)
            q |= Q(initial_set__icontains=string)
        else:
            q = Q()

        query_set = self.get_queryset(q)

        if query_set.count() == 0:
            return create_response_msg(status.HTTP_204_NO_CONTENT, 'no content')

        serializer = ProductSerializer(query_set, many=True)

        return create_response_msg(status.HTTP_200_OK, 'search result', data=serializer.data)


class ReviewList(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = (JWTAuthentication,)
    serializer_class = ReviewSerializer

    def get_product(self, pk):
        try:
            return Product.objects.get(id=pk)
        except:
            return False

    def get(self, request, product_id):
        reviews = Review.objects.filter(product_id=product_id)
        serializer = ReviewSerializer().ReviewGETSerializer(reviews, many=True)
        return create_response_msg(status.HTTP_200_OK, 'Success', serializer.data)

    def post(self, request, product_id):
        product = self.get_product(product_id)

        if not product:
            return create_response_msg(status.HTTP_204_NO_CONTENT, 'no content')
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, product=product)
            return create_response_msg(status.HTTP_201_CREATED, 'Review created', serializer.data)
        return create_response_msg(status.HTTP_400_BAD_REQUEST, 'Invalid data', request.data)


class ReviewDetail(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = (JWTAuthentication,)
    serializer_class = ReviewSerializer

    def get_review(self, pk):
        try:
            return Review.objects.get(pk=pk)
        except Review.DoesNotExist:
            return None

    def get(self, request, pk):
        review = self.get_review(pk)
        if review:
            serializer = ReviewSerializer().ReviewGETSerializer(review)
            return create_response_msg(status.HTTP_200_OK, 'Success', serializer.data)
        else:
            return create_response_msg(status.HTTP_404_NOT_FOUND, 'Review not found')

    def patch(self, request, pk):
        review = self.get_review(pk)

        if review.user != request.user:
            return create_response_msg(status.HTTP_401_UNAUTHORIZED, 'unauthorize')

        if review:
            serializer = ReviewSerializer(
                review, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return create_response_msg(status.HTTP_200_OK, 'Review updated', serializer.data)
            return create_response_msg(status.HTTP_400_BAD_REQUEST, 'Invalid data', serializer.errors)
        else:
            return create_response_msg(status.HTTP_404_NOT_FOUND, 'Review not found')

    def delete(self, request, pk):
        review = self.get_review(pk)

        if review.user != request.user:
            return create_response_msg(status.HTTP_401_UNAUTHORIZED, 'unauthorize')

        if review:
            review.delete()
            return create_response_msg(status.HTTP_204_NO_CONTENT, 'Review deleted')
        else:
            return create_response_msg(status.HTTP_404_NOT_FOUND, 'Review not found')
