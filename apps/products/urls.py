from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Category endpoints
    path('categories/', views.CategoryListCreateView.as_view(), name='category-list'),
    path('categories/<str:pk_or_slug>/', views.CategoryDetailView.as_view(), name='category-detail'),

    # Product endpoints
    path('', views.ProductListCreateView.as_view(), name='product-list'),
    path('<str:pk_or_slug>/', views.ProductDetailView.as_view(), name='product-detail'),
]
