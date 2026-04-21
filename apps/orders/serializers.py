from rest_framework import serializers
from .models import Order, OrderItem
from apps.products.serializers import ProductSerializer
from apps.users.models import Address

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'quantity', 'price', 'status', 'vendor')
        read_only_fields = ('id', 'price', 'status', 'vendor')

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source='orderitem_set', many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ('id', 'user', 'total_amount', 'status', 'shipping_address', 'items', 'created_at', 'updated_at')
        read_only_fields = ('id', 'user', 'total_amount', 'status', 'created_at', 'updated_at')

class OrderCreateSerializer(serializers.Serializer):
    shipping_address = serializers.PrimaryKeyRelatedField(queryset=Address.objects.all())

    def validate_shipping_address(self, value):
        if value.user != self.context['request'].user:
            raise serializers.ValidationError("This address does not belong to you.")
        return value

class OrderItemStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('status',)
