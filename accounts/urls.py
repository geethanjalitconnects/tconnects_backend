# accounts/urls.py

from django.urls import path
from .views import (
    RegisterView,
    PasswordLoginView,
    SendOTPView,
    VerifyOTPView,
    GoogleLoginView,
    MeView,
    LogoutView,
    CheckAuthView,
    RefreshTokenView,
    DebugView,
)

urlpatterns = [
    # Registration & Login
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', PasswordLoginView.as_view(), name='password-login'),
    
    # OTP Authentication
    path('send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    
    # Google OAuth
    path('google/', GoogleLoginView.as_view(), name='google-login'),
    
    # User Info
    path('me/', MeView.as_view(), name='me'),
    
    # Auth Status & Token Management (NEW - Safari support)
    path('check/', CheckAuthView.as_view(), name='check-auth'),
    path('refresh/', RefreshTokenView.as_view(), name='refresh-token'),
    
    # Logout
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Debug (can remove in production)
    path('debug/', DebugView.as_view(), name='debug'),
]