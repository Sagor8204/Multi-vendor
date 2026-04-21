from rest_framework import serializers
from .models import Category, Product, ProductImage

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

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
        
        # Using a simple loop or bulk_create (Note: bulk_create doesn't call save() methods)
        # If your model has custom save logic (like the ordering logic we saw), 
        # it's safer to save them individually or handle logic here.
        saved_images = []
        for img in product_images:
            img.save()
            saved_images.append(img)
            
        return saved_images

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
