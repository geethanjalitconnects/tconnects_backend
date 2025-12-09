from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings


class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that reads tokens from HTTP-only cookies
    Falls back to Authorization header if cookies not present
    """
    
    def authenticate(self, request):
        # Try to get token from cookie first
        access_token = request.COOKIES.get('access')
        
        # Fallback to Authorization header
        if not access_token:
            header = self.get_header(request)
            if header is None:
                return None
            
            raw_token = self.get_raw_token(header)
            if raw_token is None:
                return None
        else:
            raw_token = access_token
        
        # Validate the token
        try:
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)
            
            # Debug logging
            print(f"✅ Authenticated user: {user.email}")
            
            return (user, validated_token)
            
        except AuthenticationFailed as e:
            print(f"❌ Authentication failed: {str(e)}")
            # Don't raise - return None to allow AllowAny views
            return None
        except Exception as e:
            print(f"❌ Unexpected auth error: {str(e)}")
            return None