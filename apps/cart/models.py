from django.db import models
from apps.core.models import BaseModel
from apps.users.models import User
from apps.products.models import Product

# Create your models here.
class Cart(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.IntegerField()