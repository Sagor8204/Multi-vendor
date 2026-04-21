from django.urls import path
from .views import (
    RegisterView, LoginView, LogoutView, RefreshView, 
    UserProfileView, UserDetailView,
    AddressListCreateView, AddressDetailView,
    AdminUserProfileDetailView
)

urlpatterns = [
    path('register', RegisterView.as_view(), name='auth_register'),
    path('login', LoginView.as_view(), name='auth_login'),
    path('logout', LogoutView.as_view(), name='auth_logout'),
    path('refresh', RefreshView.as_view(), name='auth_refresh'),
    
    # Profile endpoints
    path('profile/me/', UserProfileView.as_view(), name='profile_me'),
    path('users/<int:user_id>/profile/', AdminUserProfileDetailView.as_view(), name='admin_user_profile'),

    path('addresses/', AddressListCreateView.as_view(), name='address_list_create'),
    path('addresses/<int:pk>/', AddressDetailView.as_view(), name='address_detail'),
    
    path('me', UserDetailView.as_view(), name='user_me'), # Existing me route using UserDetailView
    path('<int:pk>', UserDetailView.as_view(), name='user_detail'),
]
