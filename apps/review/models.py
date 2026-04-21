from django.db import models
from apps.core.models import BaseModel
from apps.users.models import User
from apps.products.models import Product

# Create your models here.
class Review(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    rating = models.IntegerField()
    comment = models.TextField()


class Wishlist(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
