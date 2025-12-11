from pathlib import Path
import dj_database_url
import os
from decouple import config, Csv
from datetime import timedelta
from corsheaders.defaults import default_headers

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv())

AUTH_USER_MODEL = 'accounts.User'

FRONTEND_URL = config('FRONTEND_URL')
ADMIN_EMAIL = config('ADMIN_EMAIL', default='tconnects@vprotectsecurity.com')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    'accounts',
    'profiles',
    'jobs',
    'internships',
    'applications',
    'courses',
    'mockinterview',
]

if DEBUG:
    try:
        import importlib
        if importlib.util.find_spec('sslserver') is not None and 'sslserver' not in INSTALLED_APPS:
            INSTALLED_APPS.append('sslserver')
    except Exception:
        pass

SITE_ID = 1
ROOT_URLCONF = 'tconnects_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'tconnects_backend.wsgi.application'

# ===========================
# MIDDLEWARE
# ===========================
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # CSRF DISABLED for API-only backend
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

if DEBUG:
    print("="*60)
    print("⚠️  CSRF MIDDLEWARE IS DISABLED")
    print("="*60)

# ===========================
# CORS CONFIGURATION - OPTIMIZED FOR SAFARI
# ===========================

CORS_ALLOW_CREDENTIALS = True

# Parse frontend URL
_frontend_url = config('FRONTEND_URL', default='').strip()

# Parse additional origins from env
_env_origins_str = config("CORS_ALLOWED_ORIGINS", default="")
_env_origins = [origin.strip() for origin in _env_origins_str.split(',') if origin.strip()]

# Build origins list
if DEBUG:
    _dev_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    all_origins = []
    if _frontend_url:
        all_origins.append(_frontend_url)
    all_origins.extend(_env_origins)
    all_origins.extend(_dev_origins)
    CORS_ALLOWED_ORIGINS = list(dict.fromkeys(all_origins))
else:
    all_origins = []
    if _frontend_url:
        all_origins.append(_frontend_url)
    all_origins.extend(_env_origins)
    CORS_ALLOWED_ORIGINS = list(dict.fromkeys(all_origins))

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS.copy()

# CRITICAL: Don't use ALLOW_ALL_CORS - causes cookie issues
CORS_ALLOW_ALL_ORIGINS = False

if DEBUG:
    print("="*60)
    print("🔒 CORS CONFIGURATION:")
    print(f"   DEBUG: {DEBUG}")
    print(f"   FRONTEND_URL: {_frontend_url}")
    print(f"   CORS_ALLOW_ALL_ORIGINS: {CORS_ALLOW_ALL_ORIGINS}")
    print(f"   CORS_ALLOWED_ORIGINS: {CORS_ALLOWED_ORIGINS}")
    print(f"   CSRF_TRUSTED_ORIGINS: {CSRF_TRUSTED_ORIGINS}")
    print(f"   CORS_ALLOW_CREDENTIALS: {CORS_ALLOW_CREDENTIALS}")
    print("="*60)

# CORS headers - ENHANCED for Safari compatibility
CORS_EXPOSE_HEADERS = [
    "Content-Type",
    "X-CSRFToken",
    "Set-Cookie",
    "Access-Control-Allow-Credentials",
    "Access-Control-Allow-Origin",
]

CORS_ALLOW_HEADERS = list(default_headers) + [
    "x-csrftoken",
    "x-requested-with",
    "content-type",
    "accept",
    "origin",
    "authorization",
    "accept-encoding",
    "access-control-allow-origin",
    "access-control-allow-credentials",
    "cookie",
    "cache-control",
    "pragma",
]

# Safari requires preflight caching
CORS_PREFLIGHT_MAX_AGE = 86400  # 24 hours

# ===========================
# COOKIE SETTINGS - SAFARI/iOS OPTIMIZED
# ===========================

# CSRF settings
CSRF_COOKIE_HTTPONLY = False
CSRF_HEADER_NAME = "X-CSRFToken"

# Session settings
SESSION_COOKIE_HTTPONLY = True

# Cookie domain - CRITICAL for Safari on subdomains
COOKIE_DOMAIN = config('COOKIE_DOMAIN', default=None)

if not DEBUG:
    # PRODUCTION: Safari-compatible settings
    # SameSite=None with Secure=True is REQUIRED for Safari cross-site cookies
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = "None"
    CSRF_COOKIE_SAMESITE = "None"
    
    # Set cookie domain for subdomain sharing
    if COOKIE_DOMAIN:
        SESSION_COOKIE_DOMAIN = COOKIE_DOMAIN
        CSRF_COOKIE_DOMAIN = COOKIE_DOMAIN
    
    # Cookie age - Safari respects these
    SESSION_COOKIE_AGE = 1209600  # 2 weeks
    SESSION_SAVE_EVERY_REQUEST = False  # Don't update session on every request
    
    # Additional security
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
else:
    # DEVELOPMENT: More permissive settings
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = "Lax"
    CSRF_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_AGE = 1209600

SECURE_CROSS_ORIGIN_OPENER_POLICY = None

# Safari cookie name must be explicit (no generic names)
SESSION_COOKIE_NAME = 'tconnects_sessionid'
CSRF_COOKIE_NAME = 'tconnects_csrftoken'

if DEBUG:
    print("="*60)
    print("🍪 COOKIE SETTINGS (Safari Optimized):")
    print(f"   SESSION_COOKIE_SECURE: {SESSION_COOKIE_SECURE}")
    print(f"   SESSION_COOKIE_SAMESITE: {SESSION_COOKIE_SAMESITE}")
    print(f"   SESSION_COOKIE_NAME: {SESSION_COOKIE_NAME}")
    print(f"   CSRF_COOKIE_SECURE: {CSRF_COOKIE_SECURE}")
    print(f"   CSRF_COOKIE_SAMESITE: {CSRF_COOKIE_SAMESITE}")
    print(f"   CSRF_COOKIE_NAME: {CSRF_COOKIE_NAME}")
    print(f"   COOKIE_DOMAIN: {COOKIE_DOMAIN}")
    print(f"   SESSION_COOKIE_AGE: {SESSION_COOKIE_AGE}s")
    print("="*60)

# ===========================
# DATABASE
# ===========================

DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True
    )
}

# ===========================
# EMAIL SETTINGS
# ===========================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER)
EMAIL_TIMEOUT = 30

if DEBUG:
    print("="*60)
    print("📧 EMAIL CONFIGURATION:")
    print(f"   EMAIL_HOST: {EMAIL_HOST}")
    print(f"   EMAIL_HOST_USER: {EMAIL_HOST_USER}")
    print(f"   EMAIL_TIMEOUT: {EMAIL_TIMEOUT}s")
    print("="*60)

# ===========================
# REST FRAMEWORK
# ===========================

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "accounts.authentication.CookieJWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "EXCEPTION_HANDLER": "rest_framework.views.exception_handler",
}

# JWT CONFIG - Enhanced for Safari
# JWT CONFIG - Enhanced for Safari
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=config('ACCESS_TOKEN_MINUTES', default=60, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=config('REFRESH_TOKEN_DAYS', default=14, cast=int)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
}
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'