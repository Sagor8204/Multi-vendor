from django.db import models
from django.contrib.auth.models import AbstractUser
from common.models.models import BaseModel

# Create your models here.
class User(AbstractUser, BaseModel):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('vendor', 'Vendor'),
        ('customer', 'Customer'),
    )

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']