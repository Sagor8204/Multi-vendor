from rest_framework import generics, status, permissions
from apps.core.utils.response import api_response
from .models import Vendor
from .serializers import VendorSerializer, VendorApplySerializer

class VendorListView(generics.ListAPIView):
    """
    List all approved vendors
    GET /api/vendors/
    """
    queryset = Vendor.objects.filter(is_active=True, is_approved=True)
    serializer_class = VendorSerializer
    permission_classes = (permissions.AllowAny,)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return api_response(
            success=True,
            message="Vendors retrieved successfully",
            data=serializer.data,
            status=status.HTTP_200_OK
        )

class VendorDetailView(generics.RetrieveAPIView):
    """
    Get vendor details by ID
    GET /api/vendors/{id}/
    """
    queryset = Vendor.objects.filter(is_active=True)
    serializer_class = VendorSerializer
    permission_classes = (permissions.AllowAny,)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return api_response(
            success=True,
            message="Vendor details retrieved successfully",
            data=serializer.data,
            status=status.HTTP_200_OK
        )

class VendorApplyView(generics.CreateAPIView):
    """
    Apply to become a vendor
    POST /api/vendors/apply/
    """
    serializer_class = VendorApplySerializer
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        if Vendor.objects.filter(user=request.user).exists():
            return api_response(
                success=False, 
                message="You have already applied or are a vendor", 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return api_response(
            success=True,
            message="Vendor application submitted successfully",
            data=serializer.data,
            status=status.HTTP_201_CREATED
        )

class VendorMeView(generics.RetrieveUpdateAPIView):
    """
    Get or update current authenticated vendor profile
    GET/PUT /api/vendors/me/
    """
    serializer_class = VendorSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        try:
            return Vendor.objects.get(user=self.request.user)
        except Vendor.DoesNotExist:
            return None

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return api_response(
                success=False, 
                message="Vendor profile not found", 
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(instance)
        return api_response(
            success=True,
            message="Your vendor profile retrieved successfully",
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return api_response(
                success=False, 
                message="Vendor profile not found", 
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return api_response(
            success=True,
            message="Vendor profile updated successfully",
            data=serializer.data,
            status=status.HTTP_200_OK
        )
