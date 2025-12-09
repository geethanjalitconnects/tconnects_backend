from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import authenticate
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail

from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from .models import User, OTP
from .serializers import RegisterSerializer, UserSerializer
from .utils import generate_otp, send_otp_email


# ---------------------------------------------------------
# TOKEN / COOKIE UTILITIES
# ---------------------------------------------------------

def get_tokens_for_user(user):
    """Generate access & refresh tokens"""
    refresh = RefreshToken.for_user(user)
    return {
        "access": refresh.access_token,
        "refresh": refresh
    }


def set_auth_cookies(response, tokens):
    """Set JWT tokens as HTTP-only cookies"""
    # Get cookie domain from settings if configured
    cookie_domain = getattr(settings, "COOKIE_DOMAIN", None)

    # Base cookie options
    cookie_options = {
        "httponly": True,
        "secure": True,
        "samesite": "None",
        "path": "/",
    }
    
    # Add domain only if configured
    if cookie_domain:
        cookie_options["domain"] = cookie_domain

    # Set access token cookie (1 hour)
    response.set_cookie(
        key="access",
        value=str(tokens["access"]),
        max_age=3600,  # 1 hour
        **cookie_options
    )

    # Set refresh token cookie (7 days)
    response.set_cookie(
        key="refresh",
        value=str(tokens["refresh"]),
        max_age=604800,  # 7 days
        **cookie_options
    )

    return response


def clear_auth_cookies(response):
    """Remove cookies on logout"""
    response.delete_cookie("access", path="/", samesite="None", secure=True)
    response.delete_cookie("refresh", path="/", samesite="None", secure=True)
    return response


# ---------------------------------------------------------
# REGISTER
# ---------------------------------------------------------

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({"errors": serializer.errors}, status=400)

        user = serializer.save()
        tokens = get_tokens_for_user(user)

        response = Response({
            "user": UserSerializer(user).data
        }, status=201)

        return set_auth_cookies(response, tokens)


# ---------------------------------------------------------
# PASSWORD LOGIN
# ---------------------------------------------------------

class PasswordLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        role = request.data.get("role")

        user = authenticate(request, email=email, password=password)

        if not user:
            return Response({"detail": "Invalid credentials"}, status=400)

        if role and user.role != role:
            return Response({"detail": f"Account is not a {role}"}, status=403)

        tokens = get_tokens_for_user(user)

        response = Response({
            "user": UserSerializer(user).data
        })

        return set_auth_cookies(response, tokens)


# ---------------------------------------------------------
# SEND OTP - FIXED VERSION
# ---------------------------------------------------------

class SendOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response({"detail": "Email is required"}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "Email not found"}, status=404)

        code = generate_otp()
        OTP.objects.create(email=email, code=code)
        
        print("="*60)
        print(f"📧 SENDING OTP")
        print(f"   To: {email}")
        print(f"   Code: {code}")
        print("="*60)
        
        # FIXED: Actually send the email synchronously
        try:
            subject = "Your TConnect Login OTP"
            message = f"""
Hello,

Your One-Time Password (OTP) for logging into TConnect is: {code}

This OTP is valid for 10 minutes.

If you didn't request this OTP, please ignore this email.

Best regards,
TConnect Team
            """.strip()
            
            result = send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            
            print(f"✅ Email sent! Result: {result}")
            return Response({"detail": "OTP sent successfully"})
            
        except Exception as exc:
            print(f"❌ EMAIL ERROR: {type(exc).__name__}: {str(exc)}")
            # Still return error so frontend knows
            return Response({
                "detail": "Failed to send OTP email. Please try again.",
                "error": str(exc)
            }, status=500)


# ---------------------------------------------------------
# VERIFY OTP LOGIN
# ---------------------------------------------------------

class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("code")

        if not email or not code:
            return Response({"detail": "Email and code are required"}, status=400)

        try:
            otp = OTP.objects.filter(email=email, code=code, is_used=False).latest("created_at")
        except OTP.DoesNotExist:
            return Response({"detail": "Invalid OTP"}, status=400)

        # Check if expired (10 minutes)
        if (timezone.now() - otp.created_at).total_seconds() > 600:
            return Response({"detail": "OTP expired"}, status=400)

        # Mark OTP as used
        otp.is_used = True
        otp.save()

        # Get user and mark as verified
        user = User.objects.get(email=email)
        user.is_verified = True
        user.save()

        # Generate tokens
        tokens = get_tokens_for_user(user)

        response = Response({
            "user": UserSerializer(user).data
        })

        return set_auth_cookies(response, tokens)


# ---------------------------------------------------------
# GOOGLE LOGIN
# ---------------------------------------------------------

class GoogleLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.data.get("id_token")

        if not token:
            return Response({"detail": "ID token is required"}, status=400)

        try:
            google_info = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['client_id']
            )

            email = google_info["email"]
            name = google_info.get("name", "")

            user, created = User.objects.get_or_create(
                email=email,
                defaults={"full_name": name, "role": "candidate", "is_verified": True}
            )

            tokens = get_tokens_for_user(user)

            response = Response({
                "user": UserSerializer(user).data
            })

            return set_auth_cookies(response, tokens)
            
        except Exception as e:
            return Response({"detail": f"Google authentication failed: {str(e)}"}, status=400)


# ---------------------------------------------------------
# CURRENT LOGGED-IN USER
# ---------------------------------------------------------

class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


# ---------------------------------------------------------
# LOGOUT
# ---------------------------------------------------------

class LogoutView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        response = Response({"detail": "Logged out"})
        return clear_auth_cookies(response)