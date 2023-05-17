from django.urls import path, include
from .views import ProductHandleApiView, ProductApiView, ProductSearchView, ReviewList, ReviewDetail


app_name = 'api'


urlpatterns = [
    path('products/', ProductApiView.as_view(), name='product'),
    path('product/<int:pk>/', ProductHandleApiView.as_view(), name='product_handle'),
    path('products/search/',
         ProductSearchView.as_view(), name='product_search'),
    path('reviews/product/<int:product_id>/',
         ReviewList.as_view(), name='review-list'),
    path('review/<int:pk>/',
         ReviewDetail.as_view(), name='review-detail'),
]
