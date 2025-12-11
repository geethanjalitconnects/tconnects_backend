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
# TOKEN / COOKIE UTILITIES - SAFARI OPTIMIZED
# ---------------------------------------------------------

def get_tokens_for_user(user):
    """Generate access & refresh tokens"""
    refresh = RefreshToken.for_user(user)
    return {
        "access": refresh.access_token,
        "refresh": refresh
    }


def set_auth_cookies(response, tokens, request=None):
    """
    Set JWT tokens as HTTP-only cookies
    SAFARI OPTIMIZED - with explicit headers and longer token lifetime
    """
    # Get cookie domain from settings (e.g., .tconnects.in)
    cookie_domain = getattr(settings, "COOKIE_DOMAIN", None)
    
    # Safari-compatible cookie options
    cookie_options = {
        "httponly": True,
        "secure": not settings.DEBUG,  # True in production (HTTPS required)
        "samesite": "None" if not settings.DEBUG else "Lax",  # None for cross-site
        "path": "/",
    }
    
    # Add domain only if configured (critical for subdomains)
    if cookie_domain:
        cookie_options["domain"] = cookie_domain
    
    # Set access token cookie (1 hour)
    response.set_cookie(
        key="access",
        value=str(tokens["access"]),
        max_age=3600,  # 1 hour
        **cookie_options
    )
    
    # Set refresh token cookie (14 days for Safari compatibility)
    response.set_cookie(
        key="refresh",
        value=str(tokens["refresh"]),
        max_age=1209600,  # 14 days (Safari works better with longer expiry)
        **cookie_options
    )
    
    # CRITICAL for Safari - Add explicit CORS headers
    if request:
        origin = request.headers.get('Origin', settings.FRONTEND_URL)
        response['Access-Control-Allow-Origin'] = origin
        response['Access-Control-Allow-Credentials'] = 'true'
    
    return response


def clear_auth_cookies(response, request=None):
    """
    Clear authentication cookies
    SAFARI OPTIMIZED - uses same settings as set_auth_cookies
    """
    # Get cookie domain from settings
    cookie_domain = getattr(settings, "COOKIE_DOMAIN", None)
    
    # Cookie deletion options - MUST match the set_cookie options
    cookie_options = {
        "path": "/",
        "samesite": "None" if not settings.DEBUG else "Lax",
        "secure": not settings.DEBUG,
    }
    
    # Add domain only if configured
    if cookie_domain:
        cookie_options["domain"] = cookie_domain
    
    # Delete both cookies with explicit settings
    response.delete_cookie("access", **cookie_options)
    response.delete_cookie("refresh", **cookie_options)
    
    # CRITICAL for Safari - Add explicit CORS headers
    if request:
        origin = request.headers.get('Origin', settings.FRONTEND_URL)
        response['Access-Control-Allow-Origin'] = origin
        response['Access-Control-Allow-Credentials'] = 'true'
    
    return response


# ---------------------------------------------------------
# REGISTER - SAFARI OPTIMIZED
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
            "user": UserSerializer(user).data,
            "message": "Registration successful"
        }, status=201)

        # Set cookies with Safari optimization
        return set_auth_cookies(response, tokens, request)


# ---------------------------------------------------------
# PASSWORD LOGIN - SAFARI OPTIMIZED
# ---------------------------------------------------------

class PasswordLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        role = request.data.get("role")

        if not email or not password:
            return Response(
                {"detail": "Email and password are required"}, 
                status=400
            )

        user = authenticate(request, email=email, password=password)

        if not user:
            return Response(
                {"detail": "Invalid credentials"}, 
                status=400
            )

        if role and user.role != role:
            return Response(
                {"detail": f"Account is not a {role}"}, 
                status=403
            )

        tokens = get_tokens_for_user(user)

        response = Response({
            "user": UserSerializer(user).data,
            "message": "Login successful"
        })

        # Set cookies with Safari optimization
        return set_auth_cookies(response, tokens, request)


# ---------------------------------------------------------
# SEND OTP - SAFARI OPTIMIZED
# ---------------------------------------------------------

class SendOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        role = request.data.get("role")  # Added role validation

        if not email:
            return Response({"detail": "Email is required"}, status=400)

        try:
            user = User.objects.get(email=email)
            
            # Validate role if provided
            if role and user.role != role:
                return Response(
                    {"detail": f"Account is not registered as {role}"}, 
                    status=403
                )
                
        except User.DoesNotExist:
            return Response(
                {"detail": "Email not found"}, 
                status=404
            )

        code = generate_otp()
        OTP.objects.create(email=email, code=code)
        
        print("="*60)
        print(f"📧 SENDING OTP")
        print(f"   To: {email}")
        print(f"   Code: {code}")
        print("="*60)
        
        # Send the email synchronously
        try:
            subject = "Your TConnects Login OTP"
            message = f"""
Hello,

Your One-Time Password (OTP) for logging into TConnects is: {code}

This OTP is valid for 10 minutes.

If you didn't request this OTP, please ignore this email.

Best regards,
TConnects Team
            """.strip()
            
            result = send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            
            print(f"✅ Email sent! Result: {result}")
            
            response = Response({
                "detail": "OTP sent successfully",
                "message": "Please check your email for the OTP"
            })
            
            # Add CORS headers for Safari
            origin = request.headers.get('Origin', settings.FRONTEND_URL)
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Credentials'] = 'true'
            
            return response
            
        except Exception as exc:
            print(f"❌ EMAIL ERROR: {type(exc).__name__}: {str(exc)}")
            return Response({
                "detail": "Failed to send OTP email. Please try again.",
                "error": str(exc)
            }, status=500)


# ---------------------------------------------------------
# VERIFY OTP LOGIN - SAFARI OPTIMIZED
# ---------------------------------------------------------

class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("code")
        role = request.data.get("role")  # Added role validation

        if not email or not code:
            return Response(
                {"detail": "Email and code are required"}, 
                status=400
            )

        try:
            otp = OTP.objects.filter(
                email=email, 
                code=code, 
                is_used=False
            ).latest("created_at")
        except OTP.DoesNotExist:
            return Response(
                {"detail": "Invalid OTP"}, 
                status=400
            )

        # Check if expired (10 minutes)
        if (timezone.now() - otp.created_at).total_seconds() > 600:
            return Response(
                {"detail": "OTP expired. Please request a new one."}, 
                status=400
            )

        # Get user
        try:
            user = User.objects.get(email=email)
            
            # Validate role if provided
            if role and user.role != role:
                return Response(
                    {"detail": f"Account is not registered as {role}"}, 
                    status=403
                )
                
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found"}, 
                status=404
            )

        # Mark OTP as used
        otp.is_used = True
        otp.save()

        # Mark user as verified
        user.is_verified = True
        user.save()

        # Generate tokens
        tokens = get_tokens_for_user(user)

        response = Response({
            "user": UserSerializer(user).data,
            "message": "Login successful"
        })

        # Set cookies with Safari optimization
        return set_auth_cookies(response, tokens, request)


# ---------------------------------------------------------
# GOOGLE LOGIN - SAFARI OPTIMIZED
# ---------------------------------------------------------

class GoogleLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.data.get("id_token")
        role = request.data.get("role", "candidate")  # Default to candidate

        if not token:
            return Response(
                {"detail": "ID token is required"}, 
                status=400
            )

        try:
            google_info = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['client_id']
            )

            email = google_info["email"]
            name = google_info.get("name", "")

            # Get or create user
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "full_name": name, 
                    "role": role, 
                    "is_verified": True
                }
            )
            
            # If user exists but role doesn't match, update it
            if not created and user.role != role:
                user.role = role
                user.save()

            tokens = get_tokens_for_user(user)

            response = Response({
                "user": UserSerializer(user).data,
                "message": "Login successful"
            })

            # Set cookies with Safari optimization
            return set_auth_cookies(response, tokens, request)
            
        except Exception as e:
            print(f"❌ Google auth error: {str(e)}")
            return Response(
                {"detail": f"Google authentication failed: {str(e)}"}, 
                status=400
            )


# ---------------------------------------------------------
# CURRENT LOGGED-IN USER - FIXED DATA STRUCTURE
# ---------------------------------------------------------

class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # ✅ FIXED: Return user data directly (not wrapped in "user" key)
        response = Response(UserSerializer(request.user).data)
        
        # Add CORS headers for Safari
        origin = request.headers.get('Origin', settings.FRONTEND_URL)
        response['Access-Control-Allow-Origin'] = origin
        response['Access-Control-Allow-Credentials'] = 'true'
        
        return response


# ---------------------------------------------------------
# CHECK AUTH STATUS - BETTER FOR INITIAL LOAD
# ---------------------------------------------------------

class CheckAuthView(APIView):
    """
    Check if user is authenticated - useful for Safari cookie verification
    Access at: /api/auth/check/
    ✅ FIXED: AllowAny so it doesn't fail when not authenticated
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        # Check if user is authenticated
        if request.user and request.user.is_authenticated:
            response = Response({
                'authenticated': True,
                'user': UserSerializer(request.user).data
            })
        else:
            response = Response({
                'authenticated': False
            })
        
        # Add CORS headers for Safari
        origin = request.headers.get('Origin', settings.FRONTEND_URL)
        response['Access-Control-Allow-Origin'] = origin
        response['Access-Control-Allow-Credentials'] = 'true'
        
        return response


# ---------------------------------------------------------
# REFRESH TOKEN - SAFARI OPTIMIZED
# ---------------------------------------------------------

class RefreshTokenView(APIView):
    """
    Refresh access token using refresh token from cookies
    Access at: /api/auth/refresh/
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh')
        
        if not refresh_token:
            return Response(
                {'error': 'Refresh token not found'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            refresh = RefreshToken(refresh_token)
            
            # Get new access token
            access_token = str(refresh.access_token)
            
            # Optionally rotate refresh token (recommended for security)
            if settings.SIMPLE_JWT.get('ROTATE_REFRESH_TOKENS', False):
                refresh.set_jti()
                refresh.set_exp()
                new_refresh_token = str(refresh)
            else:
                new_refresh_token = refresh_token
            
            response = Response({
                'message': 'Token refreshed successfully'
            })
            
            # Get cookie domain
            cookie_domain = getattr(settings, "COOKIE_DOMAIN", None)
            
            # Cookie options
            cookie_options = {
                "httponly": True,
                "secure": not settings.DEBUG,
                "samesite": "None" if not settings.DEBUG else "Lax",
                "path": "/",
            }
            
            if cookie_domain:
                cookie_options["domain"] = cookie_domain
            
            # Set new access token
            response.set_cookie(
                key="access",
                value=access_token,
                max_age=3600,
                **cookie_options
            )
            
            # Update refresh token if rotated
            if new_refresh_token != refresh_token:
                response.set_cookie(
                    key="refresh",
                    value=new_refresh_token,
                    max_age=1209600,
                    **cookie_options
                )
            
            # Add CORS headers for Safari
            origin = request.headers.get('Origin', settings.FRONTEND_URL)
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Credentials'] = 'true'
            
            return response
            
        except Exception as e:
            print(f"❌ Token refresh error: {str(e)}")
            return Response(
                {'error': 'Invalid or expired refresh token'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )


# ---------------------------------------------------------
# LOGOUT - SAFARI OPTIMIZED
# ---------------------------------------------------------

class LogoutView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # Try to blacklist the refresh token
        try:
            refresh_token = request.COOKIES.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
                print("✅ Refresh token blacklisted")
        except Exception as e:
            # Token might be invalid or already blacklisted - that's okay
            print(f"⚠️ Token blacklist warning: {str(e)}")
        
        response = Response({
            "detail": "Logged out successfully",
            "message": "You have been logged out"
        })
        
        # Clear cookies with Safari-compatible settings
        return clear_auth_cookies(response, request)


# ---------------------------------------------------------
# DEBUG VIEW - KEEP FOR TROUBLESHOOTING
# ---------------------------------------------------------

class DebugView(APIView):
    """
    Debug endpoint to check CORS, cookies, and authentication
    Access at: /api/auth/debug/
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        # Collect debug information
        debug_info = {
            "message": "Debug endpoint - checking configuration",
            "settings": {
                "DEBUG": settings.DEBUG,
                "FRONTEND_URL": settings.FRONTEND_URL,
                "COOKIE_DOMAIN": getattr(settings, 'COOKIE_DOMAIN', None),
                "CORS_ALLOW_ALL_ORIGINS": getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', False),
                "CORS_ALLOWED_ORIGINS": getattr(settings, 'CORS_ALLOWED_ORIGINS', []),
                "CORS_ALLOW_CREDENTIALS": getattr(settings, 'CORS_ALLOW_CREDENTIALS', False),
                "SESSION_COOKIE_SECURE": settings.SESSION_COOKIE_SECURE,
                "SESSION_COOKIE_SAMESITE": settings.SESSION_COOKIE_SAMESITE,
            },
            "request_info": {
                "method": request.method,
                "path": request.path,
                "origin": request.headers.get('Origin', 'Not provided'),
                "referer": request.headers.get('Referer', 'Not provided'),
                "user_agent": request.headers.get('User-Agent', 'Not provided'),
                "has_cookies": bool(request.COOKIES),
                "cookies": list(request.COOKIES.keys()),
                "is_authenticated": request.user.is_authenticated,
            }
        }
        
        # Check if user is authenticated
        if request.user.is_authenticated:
            debug_info["user"] = {
                "email": request.user.email,
                "full_name": getattr(request.user, 'full_name', 'N/A'),
                "role": getattr(request.user, 'role', 'N/A'),
            }
        
        response = Response(debug_info)
        
        # Add CORS headers
        origin = request.headers.get('Origin', settings.FRONTEND_URL)
        response['Access-Control-Allow-Origin'] = origin
        response['Access-Control-Allow-Credentials'] = 'true'
        
        return response