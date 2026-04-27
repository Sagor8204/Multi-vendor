from django.db.models import Avg
from rest_framework import serializers
from .models import Category, Product, ProductImage, ProductAttribute, ProductAttributeValue, ProductVariant, ProductSpecification
from apps.vendor.models import Vendor
from apps.review.models import Review
from apps.users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Review
        fields = "__all__"

class vendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = "__all__"

class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = (
            'id', 'name', 'slug', 'parent', 'description', 'icon', 
            'product_count', 'created_at', 'updated_at'
        )

    def get_product_count(self, obj):
        return obj.product_set.filter(status="published").count()

class ProductAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttribute
        fields = ('id', 'name')

class ProductAttributeValueSerializer(serializers.ModelSerializer):
    attribute_name = serializers.ReadOnlyField(source='attribute.name')

    class Meta:
        model = ProductAttributeValue
        fields = ('id', 'attribute', 'attribute_name', 'value')

class ProductVariantSerializer(serializers.ModelSerializer):
    attribute_values_detail = ProductAttributeValueSerializer(many=True, read_only=True, source='attribute_values')
    
    class Meta:
        model = ProductVariant
        fields = ('id', 'sku', 'price', 'stock', 'attribute_values', 'attribute_values_detail')
        extra_kwargs = {
            'attribute_values': {'write_only': True}
        }

class ProductSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSpecification
        fields = ('id', 'key', 'value')

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'product', 'image', 'alt_text', 'is_main', 'order')
        read_only_fields = ('id', 'product')

class ProductImageUploadItemSerializer(serializers.Serializer):
    image = serializers.ImageField(max_length=1000000, allow_empty_file=False, use_url=False)
    alt_text = serializers.CharField(max_length=255, required=False, allow_blank=True)
    is_main = serializers.BooleanField(default=False)
    order = serializers.IntegerField(default=0)

class ProductImageUploadSerializer(serializers.Serializer):
    images = ProductImageUploadItemSerializer(many=True, write_only=True)

    def create(self, validated_data):
        product_id = self.context.get('product_id')
        product = Product.objects.get(id=product_id)
        images_data = validated_data.get('images')
        
        product_images = []
        for item in images_data:
            product_images.append(ProductImage(
                product=product,
                image=item['image'],
                alt_text=item.get('alt_text', ''),
                is_main=item.get('is_main', False),
                order=item.get('order', 0)
            ))
        
        saved_images = []
        for img in product_images:
            img.save()
            saved_images.append(img)
            
        return saved_images

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, required=False)
    specifications = ProductSpecificationSerializer(many=True, required=False)
    vendor = vendorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)

    average_rating = serializers.SerializerMethodField()
    total_review = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id', 'vendor', 'name', 'slug', 'description', 'category',
            'price', 'discount_price', 'discount_percentage', 'stock', 'status', 'is_featured',
            'views_count', 'images', 'variants', 'specifications', 'reviews', 'average_rating', 'total_review',
            'created_at', 'updated_at'
        )
        read_only_fields = ('vendor', 'slug', 'status', 'views_count', 'discount_percentage')

    def get_average_rating(self, obj):
        average = obj.reviews.aggregate(Avg('rating')).get('rating__avg')
        return average if average else 0

    def get_total_review(self, obj):
        return obj.reviews.count()

    def create(self, validated_data):
        variants_data = validated_data.pop('variants', [])
        specs_data = validated_data.pop('specifications', [])
        
        product = Product.objects.create(**validated_data)
        
        for variant_data in variants_data:
            attr_values = variant_data.pop('attribute_values', [])
            variant = ProductVariant.objects.create(product=product, **variant_data)
            variant.attribute_values.set(attr_values)
            
        for spec_data in specs_data:
            ProductSpecification.objects.create(product=product, **spec_data)
            
        return product
