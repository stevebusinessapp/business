from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from . import api_views

app_name = 'accounts-api'

urlpatterns = [
    # Authentication endpoints
    path('auth/login/', api_views.LoginAPIView.as_view(), name='login'),
    path('auth/logout/', api_views.LogoutAPIView.as_view(), name='logout'),
    path('auth/register/', api_views.RegisterAPIView.as_view(), name='register'),
    path('auth/token/', obtain_auth_token, name='api_token_auth'),
    
    # Profile endpoints
    path('profile/', api_views.ProfileAPIView.as_view(), name='profile'),
    path('change-password/', api_views.ChangePasswordAPIView.as_view(), name='change_password'),
]
