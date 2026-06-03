from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users see conversations they are part of
        return Conversation.objects.filter(participants=self.request.user)

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        conversation = self.get_object()
        messages = conversation.messages.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def start_conversation(self, request):
        vendor_id = request.data.get('vendor_id')
        product_id = request.data.get('product_id')

        if not vendor_id:
            return Response({"error": "vendor_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if conversation already exists between this buyer, vendor (and product)
        # For simplicity, we'll just check participants and vendor
        conversation = Conversation.objects.filter(
            participants=request.user,
            vendor_id=vendor_id
        )
        
        if product_id:
            conversation = conversation.filter(product_id=product_id)
        
        conversation = conversation.first()

        if not conversation:
            from apps.vendor.models import Vendor
            try:
                vendor = Vendor.objects.get(id=vendor_id)
            except Vendor.DoesNotExist:
                return Response({"error": "Vendor not found"}, status=status.HTTP_404_NOT_FOUND)

            conversation = Conversation.objects.create(
                vendor=vendor,
                product_id=product_id
            )
            conversation.participants.add(request.user)
            # Add vendor's user as well
            conversation.participants.add(vendor.user)

        serializer = self.get_serializer(conversation)
        return Response(serializer.data)
