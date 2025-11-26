from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    PasswordLoginView,
    SendOTPView,
    VerifyOTPView,
    GoogleLoginView,
    CompleteGoogleRegistrationView,
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
    path('google/complete/', CompleteGoogleRegistrationView.as_view(), name='google-complete'),
    
    # User Info
    path('me/', MeView.as_view(), name='me'),
    
    # Logout
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Token Refresh
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]