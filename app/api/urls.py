from django.urls import path
from .views import ProductHandleApiView, ProductApiView, ProductSearchView
app_name = 'api'

urlpatterns = [
    path('product/', ProductApiView.as_view(), name='product'),
    path('product/<int:pk>/', ProductHandleApiView.as_view(), name='product_handle'),
    path('product/search/',
         ProductSearchView.as_view(), name='product_search'),

]
