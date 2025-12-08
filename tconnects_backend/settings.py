from pathlib import Path
import dj_database_url
import os
from decouple import config, Csv
from datetime import timedelta
from corsheaders.defaults import default_headers

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config("DEBUG", default=True, cast=bool)

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

# Allow sslserver during local development for HTTPS dev server
if DEBUG:
    try:
        # add sslserver if available in the virtualenv
        import importlib
        if importlib.util.find_spec('sslserver') is not None and 'sslserver' not in INSTALLED_APPS:
            INSTALLED_APPS.append('sslserver')
    except Exception:
        # silent fallback if sslserver is not installed
        pass

SITE_ID = 1
# URL configuration
ROOT_URLCONF = 'tconnects_backend.urls'

# Templates configuration (required for Django admin)
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

# WSGI application
WSGI_APPLICATION = 'tconnects_backend.wsgi.application'


MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

# ===========================
# CORS / COOKIES (FIXED VERSION)
# ===========================

CORS_ALLOW_CREDENTIALS = True

# Parse CORS origins properly
_env_origins_str = config("CORS_ALLOWED_ORIGINS", default="")
_env_origins = [origin.strip() for origin in _env_origins_str.split(',') if origin.strip()]

if DEBUG:
    # include typical local dev ports used by Vite/CRA
    _dev_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    # merge and dedupe
    CORS_ALLOWED_ORIGINS = list(dict.fromkeys(_env_origins + _dev_origins))
else:
    CORS_ALLOWED_ORIGINS = _env_origins

# CSRF trusted origins (parse properly)
_csrf_origins_str = config("CSRF_TRUSTED_ORIGINS", default="")
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in _csrf_origins_str.split(',') if origin.strip()]

# Optional: allow all origins for quick debugging/testing (use only temporarily)
ALLOW_ALL_CORS = config("ALLOW_ALL_CORS", default=False, cast=bool)
if ALLOW_ALL_CORS:
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOWED_ORIGINS = []
    print("⚠️ WARNING: ALLOW_ALL_CORS is enabled! All origins are allowed.")
else:
    CORS_ALLOW_ALL_ORIGINS = False

# Debug output to verify CORS configuration
print("="*60)
print("🔍 CORS CONFIGURATION DEBUG:")
print(f"   DEBUG mode: {DEBUG}")
print(f"   ALLOW_ALL_CORS: {ALLOW_ALL_CORS}")
print(f"   CORS_ALLOW_ALL_ORIGINS: {CORS_ALLOW_ALL_ORIGINS}")
print(f"   CORS_ALLOWED_ORIGINS: {CORS_ALLOWED_ORIGINS}")
print(f"   CSRF_TRUSTED_ORIGINS: {CSRF_TRUSTED_ORIGINS}")
print(f"   CORS_ALLOW_CREDENTIALS: {CORS_ALLOW_CREDENTIALS}")
print("="*60)

CORS_EXPOSE_HEADERS = ["Content-Type", "X-CSRFToken", "Set-Cookie"]
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

CSRF_COOKIE_HTTPONLY = False
CSRF_HEADER_NAME = "X-CSRFToken"
SESSION_COOKIE_HTTPONLY = False

# Cookie domain (leave empty for staging)
COOKIE_DOMAIN = config('COOKIE_DOMAIN', default=None)

# STAGING (DEBUG=True)
if DEBUG:
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = "Lax"
    CSRF_COOKIE_SAMESITE = "Lax"

# PRODUCTION (DEBUG=False)
else:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = "None"
    CSRF_COOKIE_SAMESITE = "None"
    SECURE_SSL_REDIRECT = True

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
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER)

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
}

# JWT CONFIG
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=config('ACCESS_TOKEN_MINUTES', default=60, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=config('REFRESH_TOKEN_DAYS', default=7, cast=int)),
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