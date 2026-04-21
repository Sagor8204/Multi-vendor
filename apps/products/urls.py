from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Category endpoints
    path('categories/', views.CategoryListCreateView.as_view(), name='category-list'),
    path('categories/<str:pk_or_slug>/', views.CategoryDetailView.as_view(), name='category-detail'),

    # Product endpoints
    path('', views.ProductListCreateView.as_view(), name='product-list'),
    path('vendor/<int:vendor_id>/', views.VendorProductListView.as_view(), name='vendor-product-list'),
    path('<str:pk_or_slug>/', views.ProductDetailView.as_view(), name='product-detail'),

    # Image management
    path('<int:product_id>/images/', views.ProductImageUploadView.as_view(), name='product-image-upload'),
    path('images/<int:image_id>/', views.ProductImageDeleteView.as_view(), name='product-image-delete'),
]
