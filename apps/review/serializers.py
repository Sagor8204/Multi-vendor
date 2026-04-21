from rest_framework import serializers
from .models import Review, Wishlist
from apps.products.serializers import ProductSerializer
from apps.products.models import Product

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Review
        fields = ('id', 'product', 'user', 'rating', 'comment', 'created_at')
        read_only_fields = ('id', 'user', 'created_at')

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

class WishlistSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )

    class Meta:
        model = Wishlist
        fields = ('id', 'product', 'product_id', 'created_at')
        read_only_fields = ('id', 'created_at')

    def validate(self, attrs):
        user = self.context['request'].user
        product = attrs['product']
        if Wishlist.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError("Product is already in your wishlist.")
        return attrs
