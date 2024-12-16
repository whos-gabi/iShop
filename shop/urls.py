from django.urls import path
from .views import product_list, contact_view, add_product

urlpatterns = [
    path('', product_list, name='product_list'),
    path('contact/', contact_view, name='contact'),
    path('add-product/', add_product, name='add_product'),
]
