from django.db import models
from django.utils.text import slugify
from apps.core.models import BaseModel
from apps.vendor.models import Vendor

# Create your models here.
class Category(BaseModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    icon = models.FileField(upload_to="category_icons/", null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(BaseModel):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('published', 'Published'),
        ('rejected', 'Rejected'),
    )

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.IntegerField(default=0)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_featured = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def discount_percentage(self):
        if self.discount_price and self.price > 0:
            discount = self.price - self.discount_price
            return round((discount / self.price) * 100, 2)
        return 0

class ProductAttribute(BaseModel):
    name = models.CharField(max_length=255) # e.g., Color, Size

    def __str__(self):
        return self.name

class ProductAttributeValue(BaseModel):
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE, related_name='values')
    value = models.CharField(max_length=255) # e.g., Red, XL

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"

class ProductVariant(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    attribute_values = models.ManyToManyField(ProductAttributeValue, related_name='variants')
    sku = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - {self.sku}"

class ProductSpecification(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specifications')
    key = models.CharField(max_length=255) # e.g., Material
    value = models.CharField(max_length=255) # e.g., Cotton

    def __str__(self):
        return f"{self.key}: {self.value}"

class ProductImage(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.FileField(upload_to='products/')
    alt_text = models.CharField(max_length=255, blank=True)
    is_main = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['product', 'order'], name='unique_product_image_order')
        ]
        ordering = ['order']

    def save(self, *args, **kwargs):
        if not self.pk and (self.order is None or self.order == 0):
            last_order = ProductImage.objects.filter(product=self.product).order_by('-order').first()
            if last_order:
                self.order = last_order.order + 1
            else:
                self.order = 1
        
        super().save(*args, **kwargs)

