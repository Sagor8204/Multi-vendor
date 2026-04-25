from rest_framework import generics, status, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Category, Product, ProductImage
from .serializers import (
    CategorySerializer, ProductSerializer, 
    ProductImageSerializer, ProductImageUploadSerializer
)
from apps.core.utils.response import api_response
from apps.vendor.models import Vendor

class CategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        queryset = Category.objects.all()
        parent_id = self.request.query_params.get('parent')
        if parent_id:
            if parent_id == 'null':
                queryset = queryset.filter(parent__isnull=True)
            else:
                queryset = queryset.filter(parent_id=parent_id)
        return queryset

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return api_response(
            success=True,
            message="Categories fetched successfully",
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return api_response(
            success=True,
            message="Category created successfully",
            data=serializer.data,
            status=status.HTTP_201_CREATED
        )

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_url_kwarg = 'pk_or_slug'

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_object(self):
        val = self.kwargs.get(self.lookup_url_kwarg)
        return get_object_or_404(Category, Q(pk=val) if val.isdigit() else Q(slug=val))

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return api_response(
            success=True,
            message="Category details fetched",
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return api_response(
            success=True,
            message="Category updated successfully",
            data=response.data,
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return api_response(
            success=True,
            message="Category deleted successfully",
            data=None,
            status=status.HTTP_204_NO_CONTENT
        )

class ProductListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        category_id = self.request.query_params.get('category')
        category_slug = self.request.query_params.get('category_slug')

        if category_id or category_slug:
            # Get the category
            if category_id:
                target_category = get_object_or_404(Category, id=category_id)
            else:
                target_category = get_object_or_404(Category, slug=category_slug)
            
            # Recursive helper to get all subcategory IDs
            def get_all_category_ids(category):
                ids = [category.id]
                for child in Category.objects.filter(parent=category):
                    ids.extend(get_all_category_ids(child))
                return ids
            
            category_ids = get_all_category_ids(target_category)
            queryset = queryset.filter(category_id__in=category_ids)

        # Search by name
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)

        return queryset

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        vendor = get_object_or_404(Vendor, user=self.request.user)
        serializer.save(vendor=vendor)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return api_response(
            success=True,
            message="Products fetched successfully",
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return api_response(
            success=True,
            message="Product created successfully",
            data=serializer.data,
            status=status.HTTP_201_CREATED
        )

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_url_kwarg = 'pk_or_slug'

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_object(self):
        val = self.kwargs.get(self.lookup_url_kwarg)
        return get_object_or_404(Product, Q(pk=val) if val.isdigit() else Q(slug=val))

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return api_response(
            success=True,
            message="Product details fetched",
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def update(self, request, *args, **kwargs):
        # Ensure only the vendor owner can update
        instance = self.get_object()
        if instance.vendor.user != self.request.user:
            return api_response(success=False, message="Permission denied", status=status.HTTP_403_FORBIDDEN)
        
        response = super().update(request, *args, **kwargs)
        return api_response(
            success=True,
            message="Product updated successfully",
            data=response.data,
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.vendor.user != self.request.user:
            return api_response(success=False, message="Permission denied", status=status.HTTP_403_FORBIDDEN)
            
        super().destroy(request, *args, **kwargs)
        return api_response(
            success=True,
            message="Product deleted successfully",
            data=None,
            status=status.HTTP_204_NO_CONTENT
        )

class VendorProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        vendor_id = self.kwargs.get('vendor_id')
        return Product.objects.filter(vendor_id=vendor_id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return api_response(
            success=True,
            message="Vendor products fetched successfully",
            data=serializer.data,
            status=status.HTTP_200_OK
        )

class ProductImageUploadView(generics.CreateAPIView):
    """
    POST: Upload multiple images for a specific product with metadata
    Example keys for form-data:
    - images[0]image (File)
    - images[0]alt_text (Text)
    - images[0]is_main (Text: true/false)
    """
    serializer_class = ProductImageUploadSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def parse_nested_data(self, data):
        """
        Helper to convert flat QueryDict into nested dictionary for images
        Converts {"images[0]image": file, "images[0]alt_text": "..."} 
        to {"images": [{"image": file, "alt_text": "..."}]}
        """
        nested_data = {"images": []}
        # Find all indices used in the request
        indices = set()
        for key in data.keys():
            if key.startswith('images[') and ']' in key:
                index = key.split('[')[1].split(']')[0]
                if index.isdigit():
                    indices.add(int(index))

        # Sort indices to maintain order
        for i in sorted(list(indices)):
            item = {}
            for field in ['image', 'alt_text', 'is_main', 'order']:
                key = f'images[{i}]{field}'
                if key in data:
                    item[field] = data[key]
            
            # Also check FILES if image is missing from data
            file_key = f'images[{i}]image'
            if file_key in self.request.FILES:
                item['image'] = self.request.FILES[file_key]
                
            if item:
                nested_data['images'].append(item)
        
        return nested_data

    def create(self, request, *args, **kwargs):
        product_id = self.kwargs.get('product_id')
        product = get_object_or_404(Product, id=product_id)

        if product.vendor.user != request.user:
            return api_response(
                success=False,
                message="You don't have permission to upload images for this product",
                status=status.HTTP_403_FORBIDDEN
            )

        # Parse the indexed data before passing to serializer
        data = self.parse_nested_data(request.data)
        
        serializer = self.get_serializer(data=data, context={'product_id': product_id})
        serializer.is_valid(raise_exception=True)
        images = serializer.save()

        return api_response(
            success=True,
            message=f"{len(images)} images uploaded successfully",
            data=ProductImageSerializer(images, many=True).data,
            status=status.HTTP_201_CREATED
        )

class ProductImageDeleteView(generics.DestroyAPIView):
    """
    DELETE: Delete a specific product image
    """
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'
    lookup_url_kwarg = 'image_id'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Check if the user is the vendor of the product
        if instance.product.vendor.user != request.user:
            return api_response(
                success=False,
                message="You don't have permission to delete this image",
                status=status.HTTP_403_FORBIDDEN
            )

        super().destroy(request, *args, **kwargs)
        return api_response(
            success=True,
            message="Image deleted successfully",
            data=None,
            status=status.HTTP_204_NO_CONTENT
        )
