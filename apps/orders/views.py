from django.db import transaction
from rest_framework import generics, status, permissions
from apps.core.utils.response import api_response
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderCreateSerializer, OrderItemStatusUpdateSerializer
from apps.cart.models import Cart, CartItem

class OrderCreateView(generics.CreateAPIView):
    """
    Create an order from cart items
    POST /api/orders/create/
    """
    serializer_class = OrderCreateSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        shipping_address = serializer.validated_data['shipping_address']
        
        # Get cart
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(cart=cart)
        except Cart.DoesNotExist:
            return api_response(success=False, message="Cart is empty", status=status.HTTP_400_BAD_REQUEST)

        if not cart_items.exists():
            return api_response(success=False, message="Cart is empty", status=status.HTTP_400_BAD_REQUEST)

        # Calculate total amount
        total_amount = sum(item.product.price * item.quantity for item in cart_items)

        # Create Order
        order = Order.objects.create(
            user=request.user,
            total_amount=total_amount,
            status='pending',
            shipping_address=shipping_address
        )

        # Create OrderItems
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                vendor=cart_item.product.vendor,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price,
                status='pending'
            )
            # Reduce stock
            product = cart_item.product
            product.stock -= cart_item.quantity
            product.save()

        # Clear cart items
        cart_items.delete()

        order_serializer = OrderSerializer(order)
        return api_response(
            success=True,
            message="Order created successfully",
            data=order_serializer.data,
            status=status.HTTP_201_CREATED
        )

class OrderListView(generics.ListAPIView):
    """
    List all orders for the current user
    GET /api/orders/
    """
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return api_response(
            success=True,
            message="Orders fetched successfully",
            data=serializer.data,
            status=status.HTTP_200_OK
        )

class OrderDetailView(generics.RetrieveAPIView):
    """
    Get order details
    GET /api/orders/{id}/
    """
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return api_response(
            success=True,
            message="Order details fetched successfully",
            data=serializer.data,
            status=status.HTTP_200_OK
        )

class OrderCancelView(generics.UpdateAPIView):
    """
    Cancel an order
    PUT /api/orders/{id}/cancel/
    """
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user, status='pending')

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = 'cancelled'
        instance.save()
        
        # Also cancel order items
        instance.orderitem_set.update(status='cancelled')
        
        # Restore stock
        for item in instance.orderitem_set.all():
            product = item.product
            product.stock += item.quantity
            product.save()

        serializer = self.get_serializer(instance)
        return api_response(
            success=True,
            message="Order cancelled successfully",
            data=serializer.data,
            status=status.HTTP_200_OK
        )

class VendorOrderListView(generics.ListAPIView):
    """
    List all orders containing items from this vendor
    GET /api/vendor/orders/
    """
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        # We assume the user is a vendor. If not, this will return empty list.
        return Order.objects.filter(orderitem__vendor__user=self.request.user).distinct().order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return api_response(
            success=True,
            message="Vendor orders fetched successfully",
            data=serializer.data,
            status=status.HTTP_200_OK
        )

class VendorOrderItemStatusUpdateView(generics.UpdateAPIView):
    """
    Update the status of an order item (by vendor)
    PUT /api/vendor/order-items/{id}/status/
    """
    serializer_class = OrderItemStatusUpdateSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return OrderItem.objects.filter(vendor__user=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return api_response(
            success=True,
            message="Order item status updated successfully",
            data=serializer.data,
            status=status.HTTP_200_OK
        )
