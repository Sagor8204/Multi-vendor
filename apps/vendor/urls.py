from django.urls import path
from .views import (
    VendorListView, VendorDetailView, 
    VendorApplyView, VendorMeView
)
from apps.products.views import VendorProductListView

urlpatterns = [
    path('', VendorListView.as_view(), name='vendor_list'),
    path('apply/', VendorApplyView.as_view(), name='vendor_apply'),
    path('me/', VendorMeView.as_view(), name='vendor_me'),
    path('<int:pk>/', VendorDetailView.as_view(), name='vendor_detail'),
    path('<int:vendor_id>/products/', VendorProductListView.as_view(), name='vendor_products'),
]
