from django.urls import path, include
from .views import ProductHandleApiView, ProductApiView, ProductSearchView


app_name = 'api'


urlpatterns = [
    path('products/', ProductApiView.as_view(), name='product'),
    path('product/<int:pk>/', ProductHandleApiView.as_view(), name='product_handle'),
    path('products/search/',
         ProductSearchView.as_view(), name='product_search'),
]
