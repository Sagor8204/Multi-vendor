from django.urls import path
from .views import RegisterView, LoginView, LogoutView, RefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('login/', LoginView.as_view(), name='auth_login'),
    path('logout/', LogoutView.as_view(), name='auth_logout'),
    path('refresh/', RefreshView.as_view(), name='auth_refresh'),
]
