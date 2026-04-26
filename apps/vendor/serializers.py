from rest_framework import serializers
from .models import Vendor
from apps.core.models import File

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['id', 'file', 'file_type']

class VendorSerializer(serializers.ModelSerializer):
    # This field handles the file upload for PUT/PATCH
    store_logo = serializers.FileField(required=False, write_only=True)
    products = serializers.SerializerMethodField()

    class Meta:
        model = Vendor
        fields = ['id', 'store_name', 'store_logo', 'store_description', 'products', 'is_approved', 'created_at']
        read_only_fields = ['id', 'is_approved', 'created_at']

    def get_products(self,obj):
        return obj.product_set.filter(vendor=obj.id).count()

    def update(self, instance, validated_data):
        user = self.context['request'].user
        # 1. Extract the file if it exists in the request
        uploaded_logo = validated_data.pop('store_logo', None)
        print(validated_data)
        if uploaded_logo:
            # 2. Create a new File record (hardcoded file_type)
            new_logo_instance = File.objects.create(
                file=uploaded_logo,
                file_type="store_logo", # Hardcoded here as well
                uploaded_by=user
            )
            # 3. Link the new file to the vendor
            instance.store_logo = new_logo_instance

        # 4. Update the rest of the fields (store_name, store_description, etc.)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """
        Ensure the response shows the full FileSerializer data 
        instead of just the file path or ID.
        """
        data = super().to_representation(instance)
        if instance.store_logo:
            data['store_logo'] = FileSerializer(instance.store_logo, context=self.context).data
        else:
            data['store_logo'] = None
        return data


class VendorApplySerializer(serializers.ModelSerializer):
    # We define this as a FileField so the serializer knows how to handle the upload
    store_logo = serializers.FileField(required=False, write_only=True)

    class Meta:
        model = Vendor
        fields = ['store_name', 'store_description', 'store_logo']

    def create(self, validated_data):
        user = self.context['request'].user
        # Extract the file from validated_data
        uploaded_logo = validated_data.pop('store_logo', None)
        
        vendor_logo_instance = None

        if uploaded_logo:
            # Create the File object first
            # .content_type gets the MIME type (e.g., 'image/svg+xml')
            vendor_logo_instance = File.objects.create(
                file=uploaded_logo,
                file_type="store_logo", 
                uploaded_by=user
            )

        # Create the vendor and link the File instance
        vendor = Vendor.objects.create(
            user=user, 
            store_logo=vendor_logo_instance,
            **validated_data
        )
        
        # Logic for user role
        if user.role != 'vendor':
            user.role = 'vendor'
            user.save()
            
        return vendor

    def to_representation(self, instance):
        """
        After the object is created, this method transforms the response.
        We use VendorSerializer to ensure store_logo returns as an object (FileSerializer)
        instead of just an ID.
        """
        data = VendorSerializer(instance, context=self.context).data
        return dict(data)
