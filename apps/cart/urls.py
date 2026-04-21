from django.urls import path
from .views import (
    CartView, AddToCartView, 
    UpdateCartItemView, RemoveFromCartView, ClearCartView
)

urlpatterns = [
    path('', CartView.as_view(), name='cart_view'),
    path('add/', AddToCartView.as_view(), name='cart_add'),
    path('update/<int:item_id>/', UpdateCartItemView.as_view(), name='cart_update'),
    path('remove/<int:item_id>/', RemoveFromCartView.as_view(), name='cart_remove'),
    path('clear/', ClearCartView.as_view(), name='cart_clear'),
]
