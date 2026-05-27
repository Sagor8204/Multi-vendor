from rest_framework import generics, status, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.db.models import Q, Min, Max, Count, Avg
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
from .models import Category, Product, ProductImage, ProductAttributeValue
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
        user = self.request.user
        
        # Base filtering for status and activity
        if user.is_authenticated:
            try:
                vendor = Vendor.objects.get(user=user)
                queryset = Product.objects.filter(
                    Q(status='published', is_active=True) | Q(vendor=vendor)
                )
            except Vendor.DoesNotExist:
                queryset = Product.objects.filter(status='published', is_active=True)
        else:
            queryset = Product.objects.filter(status='published', is_active=True)

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

        # --- Filtering & Sorting Flags ---

        # 1. Featured Products
        featured = self.request.query_params.get('featured')
        if featured == 'true':
            queryset = queryset.filter(is_featured=True)

        # 2. On Sale (Products with discounts)
        on_sale = self.request.query_params.get('on_sale')
        if on_sale == 'true':
            queryset = queryset.filter(discount_price__isnull=False, discount_price__gt=0)

        # 3. New Arrivals (Last 30 days)
        new_arrivals = self.request.query_params.get('new_arrivals')
        if new_arrivals == 'true':
            from django.utils import timezone
            from datetime import timedelta
            thirty_days_ago = timezone.now() - timedelta(days=30)
            queryset = queryset.filter(created_at__gte=thirty_days_ago)

        # 4. Trending (Sorting by views)
        trending = self.request.query_params.get('trending')
        if trending == 'true':
            queryset = queryset.order_by('-views_count')
        
        # Generic ordering
        ordering = self.request.query_params.get('ordering')
        if ordering:
            queryset = queryset.order_by(ordering)

        return queryset.distinct()

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        vendor = get_object_or_404(Vendor, user=self.request.user)
        # Products created by vendors default to 'pending' status
        serializer.save(vendor=vendor, status='pending')

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
            message="Product created successfully and is pending approval",
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
        user = self.request.user
        
        product = get_object_or_404(Product, Q(pk=val) if val.isdigit() else Q(slug=val))
        
        # If not published/active, only the owner or admin can see it
        if product.status != 'published' or not product.is_active:
            if not user.is_authenticated or (product.vendor.user != user and not user.is_staff):
                from django.http import Http404
                raise Http404
        
        # Increment view count on retrieve
        if self.request.method == 'GET':
            product.views_count += 1
            product.save(update_fields=['views_count'])
            
        return product

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
        
        # If product was rejected or published, any update might need re-approval
        # For now, let's just keep the status as is unless we want to force re-approval
        
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
        user = self.request.user
        
        queryset = Product.objects.filter(vendor_id=vendor_id)
        
        # Check if the requesting user is the owner of this vendor
        is_owner = False
        if user.is_authenticated:
            try:
                vendor = Vendor.objects.get(user=user)
                if vendor.id == int(vendor_id):
                    is_owner = True
            except (Vendor.DoesNotExist, ValueError):
                pass
        
        if not is_owner:
            queryset = queryset.filter(status='published', is_active=True)
            
        return queryset

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

class ProductSearchView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Product.objects.filter(status='published', is_active=True)
        
        # Search by name and description
        query = self.request.query_params.get('q')
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query)
            )

        # Filter by category
        category_slug = self.request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        # Ordering
        sort = self.request.query_params.get('sort')
        if sort == 'price_low':
            queryset = queryset.order_by('price')
        elif sort == 'price_high':
            queryset = queryset.order_by('-price')
        elif sort == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort == 'popular':
            queryset = queryset.order_by('-views_count')
        
        return queryset.distinct()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return api_response(
            success=True,
            message="Search results fetched successfully",
            data=serializer.data,
            status=status.HTTP_200_OK
        )

class AdvancedProductSearchView(generics.ListAPIView):
    """
    Advanced search with typo tolerance and faceted aggregations.
    """
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Product.objects.filter(status='published', is_active=True).annotate(
            avg_rating=Avg('reviews__rating')
        )
        query = self.request.query_params.get('q')

        if query:
            # 1. Try Full-Text Search first
            vector = SearchVector('name', weight='A') + SearchVector('description', weight='B')
            search_query = SearchQuery(query)
            
            fts_queryset = queryset.annotate(
                rank=SearchRank(vector, search_query)
            ).filter(rank__gte=0.1).order_by('-rank')

            # 2. If FTS finds nothing, use Trigram Similarity for typo tolerance
            if not fts_queryset.exists():
                queryset = queryset.annotate(
                    similarity=TrigramSimilarity('name', query)
                ).filter(similarity__gt=0.2).order_by('-similarity')
            else:
                queryset = fts_queryset

        # Filter by category
        category_slug = self.request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        # Filter by Color
        colors = self.request.query_params.getlist('color') + self.request.query_params.getlist('color[]')
        if colors:
            color_list = []
            for c in colors:
                color_list.extend(c.split(','))
            queryset = queryset.filter(variants__attribute_values__value__in=color_list, variants__attribute_values__attribute__name__iexact='Color')

        # Filter by Size
        sizes = self.request.query_params.getlist('size') + self.request.query_params.getlist('size[]')
        if sizes:
            size_list = []
            for s in sizes:
                size_list.extend(s.split(','))
            queryset = queryset.filter(variants__attribute_values__value__in=size_list, variants__attribute_values__attribute__name__iexact='Size')

        # Filter by Rating (e.g., ?rating=4 means 4 stars and up)
        ratings = self.request.query_params.getlist('rating') + self.request.query_params.getlist('rating[]')
        if ratings:
            rating_list = []
            for r in ratings:
                rating_list.extend(r.split(','))
            try:
                min_rating = min([float(r) for r in rating_list])
                queryset = queryset.filter(avg_rating__gte=min_rating)
            except (ValueError, TypeError):
                pass

        # Generic Attribute Filter (Fallback)
        attr_values = self.request.query_params.getlist('attribute_value')
        if attr_values:
            for val in attr_values:
                queryset = queryset.filter(variants__attribute_values__value__iexact=val)

        # Ordering
        sort = self.request.query_params.get('sort')
        if sort == 'price_low':
            queryset = queryset.order_by('price')
        elif sort == 'price_high':
            queryset = queryset.order_by('-price')
        elif sort == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort == 'popular':
            queryset = queryset.order_by('-views_count')
        elif sort == 'rating':
            queryset = queryset.order_by('-avg_rating')
        # If no explicit sort is provided but there is a query, 
        # the queryset is already ordered by rank/similarity from the search block.

        return queryset.distinct()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # Calculate Facets before pagination
        facets = self.get_facets(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response_data = {
                'results': serializer.data,
                'facets': facets
            }
            return self.get_paginated_response(response_data)

        serializer = self.get_serializer(queryset, many=True)
        return api_response(
            success=True,
            message="Advanced search results fetched successfully",
            data={
                'results': serializer.data,
                'facets': facets
            },
            status=status.HTTP_200_OK
        )

    def get_facets(self, queryset):
        # 1. Price Range
        price_range = queryset.aggregate(
            min=Min('price'),
            max=Max('price')
        )

        # 2. Categories
        categories = Category.objects.filter(
            product__in=queryset
        ).annotate(
            count=Count('product')
        ).values('id', 'name', 'slug', 'count').order_by('-count')

        # 3. Attributes
        attributes = {}
        attr_values = ProductAttributeValue.objects.filter(
            variants__product__in=queryset
        ).select_related('attribute').annotate(
            count=Count('variants__product', distinct=True)
        ).order_by('attribute__name', '-count')

        for val in attr_values:
            attr_name = val.attribute.name
            if attr_name not in attributes:
                attributes[attr_name] = []
            attributes[attr_name].append({
                'id': val.id,
                'value': val.value,
                'count': val.count
            })

        # 4. Ratings
        rating_facets = []
        for i in range(1, 6):
            count = queryset.filter(avg_rating__gte=i).count()
            rating_facets.append({
                'rating': i,
                'count': count
            })

        return {
            'price_range': price_range,
            'categories': list(categories),
            'attributes': attributes,
            'ratings': rating_facets
        }
