from django.contrib import admin
from .models import (
    Category, Product, ProductImage, 
    ProductAttribute, ProductAttributeValue, 
    ProductVariant, ProductSpecification
)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent')
    prepopulated_fields = {'slug': ('name',)}

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    filter_horizontal = ('attribute_values',)

class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'vendor', 'price', 'stock', 'category', 'is_featured')
    list_filter = ('status', 'is_featured', 'category', 'vendor')
    search_fields = ('name', 'slug', 'vendor__shop_name')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductVariantInline, ProductSpecificationInline]
    actions = ['make_published', 'make_rejected']

    def make_published(self, request, queryset):
        queryset.update(status='published')
    make_published.short_description = "Mark selected products as Published"

    def make_rejected(self, request, queryset):
        queryset.update(status='rejected')
    make_rejected.short_description = "Mark selected products as Rejected"

@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(ProductAttributeValue)
class ProductAttributeValueAdmin(admin.ModelAdmin):
    list_display = ('attribute', 'value')
    list_filter = ('attribute',)

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'sku', 'price', 'stock')
    search_fields = ('sku', 'product__name')

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image', 'is_main', 'order')
