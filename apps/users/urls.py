from django.urls import path
from .views import RegisterView, LoginView, LogoutView, RefreshView, UserProfileView, UserDetailView

urlpatterns = [
    path('register', RegisterView.as_view(), name='auth_register'),
    path('login', LoginView.as_view(), name='auth_login'),
    path('logout', LogoutView.as_view(), name='auth_logout'),
    path('refresh', RefreshView.as_view(), name='auth_refresh'),
    path('me', UserProfileView.as_view(), name='user_me'),
    path('<int:pk>', UserDetailView.as_view(), name='user_detail'),
]
