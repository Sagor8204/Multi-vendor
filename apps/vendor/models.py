from django.db import models
from apps.core.models import BaseModel
from apps.users.models import User

# Create your models here.
class Vendor(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    store_name = models.CharField(max_length=255)
    store_logo = models.ForeignKey('core.File', on_delete=models.SET_NULL, null=True)
    store_description = models.TextField()
    is_approved = models.BooleanField(default=False)