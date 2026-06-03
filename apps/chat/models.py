from django.db import models
from apps.core.models import BaseModel
from apps.users.models import User
from apps.vendor.models import Vendor
from apps.products.models import Product

class Conversation(BaseModel):
    participants = models.ManyToManyField(User, related_name='conversations')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='vendor_conversations')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='product_inquiries')

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Conversation between {', '.join([u.email for u in self.participants.all()])} and {self.vendor.store_name}"

class Message(BaseModel):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message from {self.sender.email} at {self.created_at}"
