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


# ==========================================================
# COOKIE HELPERS
# ==========================================================

COOKIE_DOMAIN = ".onrender.com"   # REQUIRED FOR RENDER CROSS-DOMAIN


def set_auth_cookies(response, tokens):
    """Set secure HttpOnly cookies for access & refresh tokens."""

    # ACCESS TOKEN (1 hr)
    response.set_cookie(
        key="access",
        value=str(tokens["access"]),
        httponly=True,
        secure=True,
        samesite="None",
        domain=COOKIE_DOMAIN,
        max_age=3600,
    )

    # REFRESH TOKEN (7 days)
    response.set_cookie(
        key="refresh",
        value=str(tokens["refresh"]),
        httponly=True,
        secure=True,
        samesite="None",
        domain=COOKIE_DOMAIN,
        max_age=3600 * 24 * 7,
    )

    return response


def clear_auth_cookies(response):
    """Remove cookies on logout."""
    response.delete_cookie("access", domain=COOKIE_DOMAIN, samesite="None")
    response.delete_cookie("refresh", domain=COOKIE_DOMAIN, samesite="None")
    return response


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "access": refresh.access_token,
        "refresh": refresh,
    }


# ==========================================================
# REGISTER
# ==========================================================

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():

            email = serializer.validated_data.get("email")
            role = serializer.validated_data.get("role")

            if User.objects.filter(email=email).exists():
                return Response(
                    {"errors": {"email": ["User with this email already exists."]}},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Recruiters must use company email
            if role == "recruiter":
                personal_domains = [
                    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
                    "aol.com", "icloud.com", "mail.com", "protonmail.com"
                ]
                if email.split("@")[-1].lower() in personal_domains:
                    return Response(
                        {"errors": {"email": ["Recruiters must use a company email."]}},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            user = serializer.save()
            tokens = get_tokens_for_user(user)

            response = Response(
                {"user": UserSerializer(user).data},
                status=status.HTTP_201_CREATED,
            )

            return set_auth_cookies(response, tokens)

        return Response(
            {"errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


# ==========================================================
# PASSWORD LOGIN
# ==========================================================

class PasswordLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        role = request.data.get("role")

        if not email or not password:
            return Response(
                {"detail": "Email and password are required"},
                status=400,
            )

        user = authenticate(request, email=email, password=password)

        if user is None:
            return Response(
                {"detail": "Invalid email or password"},
                status=400,
            )

        if role and user.role != role:
            return Response(
                {"detail": f"This account is not registered as a {role}"},
                status=403,
            )

        tokens = get_tokens_for_user(user)

        response = Response({"user": UserSerializer(user).data})
        return set_auth_cookies(response, tokens)


# ==========================================================
# SEND OTP
# ==========================================================

class SendOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        role = request.data.get("role")

        if not email:
            return Response({"detail": "Email is required"}, status=400)

        try:
            user = User.objects.get(email=email)

            if role and user.role != role:
                return Response(
                    {"detail": f"This account is not registered as a {role}"},
                    status=403,
                )

        except User.DoesNotExist:
            return Response(
                {"detail": "No account found with this email"},
                status=404,
            )

        code = generate_otp()
        OTP.objects.create(email=email, code=code)
        send_otp_email(email, code)

        return Response({"detail": "OTP sent successfully"})


# ==========================================================
# VERIFY OTP LOGIN
# ==========================================================

class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("code")
        role = request.data.get("role")

        if not email or not code:
            return Response({"detail": "Email and OTP required"}, status=400)

        try:
            otp = OTP.objects.filter(
                email=email,
                code=code,
                is_used=False
            ).latest("created_at")

        except OTP.DoesNotExist:
            return Response({"detail": "Invalid or expired OTP"}, status=400)

        # Check expiry (10 min)
        if (timezone.now() - otp.created_at).total_seconds() > 600:
            return Response({"detail": "OTP expired"}, status=400)

        otp.is_used = True
        otp.save()

        try:
            user = User.objects.get(email=email)

            if role and user.role != role:
                return Response(
                    {"detail": f"This account is not registered as a {role}"},
                    status=403,
                )

        except User.DoesNotExist:
            return Response({"detail": "User not found"}, status=404)

        user.is_verified = True
        user.save()

        tokens = get_tokens_for_user(user)

        response = Response({"user": UserSerializer(user).data})
        return set_auth_cookies(response, tokens)


# ==========================================================
# GOOGLE LOGIN
# ==========================================================

class GoogleLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):

        id_token_received = request.data.get("id_token")

        if not id_token_received:
            return Response({"detail": "Missing Google ID token"}, status=400)

        try:
            google_info = id_token.verify_oauth2_token(
                id_token_received,
                google_requests.Request(),
                settings.SOCIALACCOUNT_PROVIDERS["google"]["APP"]["client_id"],
            )
        except:
            return Response({"detail": "Invalid Google token"}, status=400)

        email = google_info.get("email")
        full_name = google_info.get("name", "")
        role = request.data.get("role", "candidate")

        user, _ = User.objects.get_or_create(
            email=email,
            defaults={
                "full_name": full_name,
                "role": role,
                "is_verified": True,
            },
        )

        tokens = get_tokens_for_user(user)

        response = Response({"user": UserSerializer(user).data})
        return set_auth_cookies(response, tokens)


# ==========================================================
# CURRENT LOGGED-IN USER
# ==========================================================

class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


# ==========================================================
# LOGOUT
# ==========================================================

class LogoutView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        response = Response({"detail": "Logged out"})
        return clear_auth_cookies(response)
