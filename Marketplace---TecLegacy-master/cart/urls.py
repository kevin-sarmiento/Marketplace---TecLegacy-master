from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/process/<int:order_id>/', views.payment_process, name='payment_process'),
    path('payment/execute/<int:order_id>/', views.payment_execute, name='payment_execute'),
    path('payment/success/<int:order_id>/', views.payment_success, name='payment_success'),
    path('payment/cancel/<int:order_id>/', views.payment_cancel, name='payment_cancel'),
]