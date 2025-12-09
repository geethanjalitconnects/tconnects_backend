from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    PasswordLoginView,
    SendOTPView,
    VerifyOTPView,
    GoogleLoginView,
    MeView,
    LogoutView
)

app_name = 'accounts'

urlpatterns = [
    # Registration
    path('register/', RegisterView.as_view(), name='register'),
    
    # Password Login
    path('login/', PasswordLoginView.as_view(), name='login'),
    
    # OTP Authentication
    path('send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    
    # Google OAuth
    path('google/login/', GoogleLoginView.as_view(), name='google-login'),
    # ❌ Removed google/complete (No longer needed)

    # User Info
    path('me/', MeView.as_view(), name='me'),
    
    # Logout
    path('logout/', LogoutView.as_view(), name='logout'),
    path('debug/', DebugView.as_view(), name='debug'),
    
    # Token Refresh (not used in cookie auth but safe to keep)
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]
