from rest_framework import serializers
from .models import Cart, CartItem
from apps.products.models import Product
from apps.products.serializers import ProductSerializer

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    sub_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'quantity', 'sub_total')

    def get_sub_total(self, obj):
        return obj.product.price * obj.quantity

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(source='cartitem_set', many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ('id', 'items', 'total_price', 'total_items')

    def get_total_price(self, obj):
        return sum(item.product.price * item.quantity for item in obj.cartitem_set.all())

    def get_total_items(self, obj):
        return sum(item.quantity for item in obj.cartitem_set.all())

class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(default=1, min_value=1)

    def validate(self, attrs):
        product = attrs['product_id']
        quantity = attrs['quantity']
        
        # Get user from context
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return attrs
            
        cart, _ = Cart.objects.get_or_create(user=request.user)
        existing_item = CartItem.objects.filter(cart=cart, product=product).first()
        
        total_quantity = quantity + (existing_item.quantity if existing_item else 0)
        
        if total_quantity > product.stock:
            raise serializers.ValidationError({
                "quantity": f"Insufficient stock. Only {product.stock} items available."
            })
            
        return attrs

class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ('quantity',)
        extra_kwargs = {
            'quantity': {'min_value': 1}
        }

    def validate_quantity(self, value):
        if value > self.instance.product.stock:
             raise serializers.ValidationError(f"Insufficient stock. Only {self.instance.product.stock} items available.")
        return value
