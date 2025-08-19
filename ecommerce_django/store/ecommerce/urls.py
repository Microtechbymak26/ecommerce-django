
from django.urls import path
from . import views

urlpatterns = [
path('', views.home, name='home'),  # Assuming 'home' is the view function in ecommerce app
path("shop/", views.shop, name="shop"),  # Shop page
path('product/<slug:slug>/', views.product_detail, name='product_detail'),
path('cart/add/', views.add_to_cart, name='add_to_cart'),
path('cart/', views.cart, name='cart'),
# urls.py
path('delete-cart-item/', views.delete_cart_item, name='delete_cart_item'),
path('create_order/', views.create_order, name='create_order'),
# urls.py
path('checkout/<int:order_id>/', views.checkout, name='checkout')
]
