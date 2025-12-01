from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import authenticate
from django.utils import timezone
from django.conf import settings

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
    """Attach secure cookies for authentication"""

    # Access token — 1 hour
    response.set_cookie(
        key="access",
        value=str(tokens["access"]),
        httponly=True,
        secure=True,
        samesite="None",
        max_age=3600,
        path="/"
    )

    # Refresh token — 7 days
    response.set_cookie(
        key="refresh",
        value=str(tokens["refresh"]),
        httponly=True,
        secure=True,
        samesite="None",
        max_age=3600 * 24 * 7,
        path="/"
    )

    return response


def clear_auth_cookies(response):
    """Remove cookies on logout"""
    response.delete_cookie("access", path="/")
    response.delete_cookie("refresh", path="/")
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
# SEND OTP
# ---------------------------------------------------------

class SendOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "Email not found"}, status=404)

        code = generate_otp()
        OTP.objects.create(email=email, code=code)

        send_otp_email(email, code)

        return Response({"detail": "OTP sent"})


# ---------------------------------------------------------
# VERIFY OTP LOGIN
# ---------------------------------------------------------

class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("code")

        try:
            otp = OTP.objects.filter(email=email, code=code, is_used=False).latest("created_at")
        except OTP.DoesNotExist:
            return Response({"detail": "Invalid OTP"}, status=400)

        # Expired?
        if (timezone.now() - otp.created_at).total_seconds() > 600:
            return Response({"detail": "OTP expired"}, status=400)

        otp.is_used = True
        otp.save()

        user = User.objects.get(email=email)
        user.is_verified = True
        user.save()

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
