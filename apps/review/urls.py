from django.urls import path
from . import views

urlpatterns = [
    # Review endpoints
    path('reviews/', views.ReviewCreateView.as_view(), name='review-create'),
    
    # Wishlist endpoints
    path('wishlist/', views.WishlistListView.as_view(), name='wishlist-list'),
    path('wishlist/add/', views.WishlistAddView.as_view(), name='wishlist-add'),
    path('wishlist/remove/<int:product_id>/', views.WishlistRemoveView.as_view(), name='wishlist-remove'),
]
