from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from .serializers import (
    CartSerializer, AddToCartSerializer, 
    UpdateCartItemSerializer, CartItemSerializer
)
from apps.products.models import Product
from apps.core.utils.response import api_response

class CartView(generics.RetrieveAPIView):
    """
    GET: Get current user's cart
    """
    serializer_class = CartSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return api_response(
            success=True,
            message="Cart fetched successfully",
            data=serializer.data,
            status=status.HTTP_200_OK
        )

class AddToCartView(APIView):
    """
    POST: Add product to cart
    """
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = AddToCartSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        product = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']

        cart, created = Cart.objects.get_or_create(user=request.user)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return api_response(
            success=True,
            message="Item added to cart",
            data=CartItemSerializer(cart_item).data,
            status=status.HTTP_201_CREATED
        )

class UpdateCartItemView(generics.UpdateAPIView):
    """
    PUT: Update cart item quantity
    """
    serializer_class = UpdateCartItemSerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'pk'
    lookup_url_kwarg = 'item_id'

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return api_response(
            success=True,
            message="Cart item updated",
            data=response.data,
            status=status.HTTP_200_OK
        )

class RemoveFromCartView(generics.DestroyAPIView):
    """
    DELETE: Remove item from cart
    """
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'pk'
    lookup_url_kwarg = 'item_id'

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return api_response(
            success=True,
            message="Item removed from cart",
            data=None,
            status=status.HTTP_204_NO_CONTENT
        )

class ClearCartView(APIView):
    """
    DELETE: Clear entire cart
    """
    permission_classes = (permissions.IsAuthenticated,)

    def delete(self, request):
        cart = get_object_or_404(Cart, user=request.user)
        cart.cartitem_set.all().delete()
        
        return api_response(
            success=True,
            message="Cart cleared successfully",
            data=None,
            status=status.HTTP_204_NO_CONTENT
        )
