from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search_products, name='search'),
    path('products/', views.product_list, name='product_list'),
    path('products/<slug:category_slug>/', views.product_list, name='products_by_category'),
    path('products/<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),
]