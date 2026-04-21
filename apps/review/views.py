from rest_framework import generics, status, permissions
from apps.core.utils.response import api_response
from .models import Review, Wishlist
from .serializers import ReviewSerializer, WishlistSerializer
from apps.products.models import Product

class ReviewCreateView(generics.CreateAPIView):
    """
    Submit a product review
    POST /api/reviews/
    """
    serializer_class = ReviewSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return api_response(
            success=True,
            message="Review submitted successfully",
            data=response.data,
            status=status.HTTP_201_CREATED
        )

class ProductReviewListView(generics.ListAPIView):
    """
    Get reviews for a specific product
    GET /api/products/{product_id}/reviews/
    """
    serializer_class = ReviewSerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        return Review.objects.filter(product_id=product_id).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return api_response(
            success=True,
            message="Product reviews fetched successfully",
            data=serializer.data,
            status=status.HTTP_200_OK
        )

class WishlistListView(generics.ListAPIView):
    """
    Get current user's wishlist
    GET /api/wishlist/
    """
    serializer_class = WishlistSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return api_response(
            success=True,
            message="Wishlist items fetched successfully",
            data=serializer.data,
            status=status.HTTP_200_OK
        )

class WishlistAddView(generics.CreateAPIView):
    """
    Add a product to wishlist
    POST /api/wishlist/add/
    """
    serializer_class = WishlistSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return api_response(
            success=True,
            message="Product added to wishlist",
            data=response.data,
            status=status.HTTP_201_CREATED
        )

class WishlistRemoveView(generics.DestroyAPIView):
    """
    Remove a product from wishlist
    DELETE /api/wishlist/remove/{product_id}/
    """
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'product_id'

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return api_response(
            success=True,
            message="Product removed from wishlist",
            data=None,
            status=status.HTTP_204_NO_CONTENT
        )
