from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.conf import settings
from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from .models import User, OTP
from .serializers import RegisterSerializer, UserSerializer
from .utils import generate_otp, send_otp_email


def get_tokens_for_user(user):
    """Generate JWT tokens for a user"""
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh)
    }


class RegisterView(APIView):
    """Handle user registration with email and password"""
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            role = serializer.validated_data.get("role")

            # Check if user already exists
            if User.objects.filter(email=email).exists():
                return Response(
                    {"errors": {"email": ["User with this email already exists."]}},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Recruiter domain validation
            if role == "recruiter":
                personal_domains = [
                    'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
                    'aol.com', 'icloud.com', 'mail.com', 'protonmail.com'
                ]
                domain = email.split("@")[-1].lower()
                if domain in personal_domains:
                    return Response(
                        {"errors": {"email": ["Recruiters must use a company email address."]}},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Create user
            user = serializer.save()
            
            # Generate tokens
            tokens = get_tokens_for_user(user)
            
            return Response(
                {
                    "tokens": tokens,
                    "user": UserSerializer(user).data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {"errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


class PasswordLoginView(APIView):
    """Handle password-based login"""
    
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        role = request.data.get("role")

        if not email or not password:
            return Response(
                {"detail": "Email and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, email=email, password=password)
        
        if user is None:
            return Response(
                {"detail": "Invalid email or password"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify role matches
        if role and user.role != role:
            return Response(
                {"detail": f"This account is not registered as a {role}"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Admin email check
        if user.role == "admin" and user.email != settings.ADMIN_EMAIL:
            return Response(
                {"detail": "Unauthorized admin access"},
                status=status.HTTP_403_FORBIDDEN
            )

        tokens = get_tokens_for_user(user)
        
        return Response({
            "tokens": tokens,
            "user": UserSerializer(user).data
        })


class SendOTPView(APIView):
    """Send OTP to user's email"""
    
    def post(self, request):
        email = request.data.get("email")
        role = request.data.get("role")
        
        if not email:
            return Response(
                {"detail": "Email is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user exists
        try:
            user = User.objects.get(email=email)
            
            # Verify role matches
            if role and user.role != role:
                return Response(
                    {"detail": f"This account is not registered as a {role}"},
                    status=status.HTTP_403_FORBIDDEN
                )
        except User.DoesNotExist:
            return Response(
                {"detail": "No account found with this email. Please register first."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Generate and send OTP
        code = generate_otp()
        OTP.objects.create(email=email, code=code)
        send_otp_email(email, code)

        return Response({"detail": "OTP sent successfully"})


class VerifyOTPView(APIView):
    """Verify OTP and log in user"""
    
    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("code")
        role = request.data.get("role")

        if not email or not code:
            return Response(
                {"detail": "Email and OTP are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Find valid OTP
        try:
            otp = OTP.objects.filter(
                email=email,
                code=code,
                is_used=False
            ).latest("created_at")
        except OTP.DoesNotExist:
            return Response(
                {"detail": "Invalid or expired OTP"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check expiry (10 minutes)
        if (timezone.now() - otp.created_at).total_seconds() > 600:
            return Response(
                {"detail": "OTP has expired. Please request a new one."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Mark OTP as used
        otp.is_used = True
        otp.save()

        # Get user
        try:
            user = User.objects.get(email=email)
            
            # Verify role matches
            if role and user.role != role:
                return Response(
                    {"detail": f"This account is not registered as a {role}"},
                    status=status.HTTP_403_FORBIDDEN
                )
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Mark user as verified
        user.is_verified = True
        user.save()

        # Admin check
        if user.role == "admin" and user.email != settings.ADMIN_EMAIL:
            return Response(
                {"detail": "Unauthorized admin access"},
                status=status.HTTP_403_FORBIDDEN
            )

        tokens = get_tokens_for_user(user)

        return Response({
            "tokens": tokens,
            "user": UserSerializer(user).data
        })


class GoogleLoginView(APIView):
    """Handle Google OAuth login"""
    
    def get(self, request):
        """Redirect to Google OAuth"""
        user_type = request.GET.get('user_type', 'candidate')
        # Store user_type in session for callback
        request.session['pending_user_type'] = user_type
        
        # In production, use django-allauth's redirect
        # For now, return instruction
        return Response({
            "detail": "Configure django-allauth Google provider in settings"
        })
    
    def post(self, request):
        """Verify Google ID token"""
        id_token_received = request.data.get("id_token")
        
        if not id_token_received:
            return Response(
                {"detail": "No ID token provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            google_info = id_token.verify_oauth2_token(
                id_token_received,
                google_requests.Request(),
                settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['client_id']
            )
        except Exception as e:
            return Response(
                {"detail": "Invalid Google token"},
                status=status.HTTP_400_BAD_REQUEST
            )

        email = google_info.get("email")
        full_name = google_info.get("name", "")
        role = request.data.get("role", "candidate")

        # Get or create user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "full_name": full_name,
                "role": role,
                "is_verified": True
            }
        )

        # If user exists but role doesn't match
        if not created and user.role != role:
            return Response(
                {"detail": f"This account is registered as a {user.role}, not {role}"},
                status=status.HTTP_403_FORBIDDEN
            )

        tokens = get_tokens_for_user(user)
        
        return Response({
            "tokens": tokens,
            "user": UserSerializer(user).data,
            "new_user": created
        })


class CompleteGoogleRegistrationView(APIView):
    """Complete registration for Google users who need additional info"""
    
    def post(self, request):
        email = request.data.get("email")
        full_name = request.data.get("full_name")
        role = request.data.get("role")

        if not (email and role):
            return Response(
                {"detail": "Email and role are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Recruiter domain check
        if role == "recruiter":
            personal_domains = [
                'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
                'aol.com', 'icloud.com', 'mail.com', 'protonmail.com'
            ]
            domain = email.split("@")[-1].lower()
            if domain in personal_domains:
                return Response(
                    {"detail": "Recruiters must use a company email address"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Update user
        user.role = role
        if full_name:
            user.full_name = full_name
        user.is_verified = True
        user.save()

        tokens = get_tokens_for_user(user)
        
        return Response({
            "tokens": tokens,
            "user": UserSerializer(user).data
        })


class MeView(APIView):
    """Get current user information"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class LogoutView(APIView):
    """Handle user logout"""
    
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            pass
        
        return Response(
            {"detail": "Successfully logged out"},
            status=status.HTTP_200_OK
        )