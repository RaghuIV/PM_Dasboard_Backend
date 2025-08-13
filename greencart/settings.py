"""
Django settings for greencart project (Render-ready).
"""

from pathlib import Path
import os
from datetime import timedelta
from dotenv import load_dotenv
import dj_database_url

load_dotenv()

# ------------------------------------------------------
# Paths
# ------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# Small helper for comma-separated env lists
def env_list(key: str, default: str = ""):
    raw = os.getenv(key, default)
    return [s.strip() for s in raw.split(",") if s.strip()]

# ------------------------------------------------------
# Core security / debug
# ------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-unsafe-key")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "localhost,127.0.0.1")

# If your app sits behind a proxy (Render), trust X-Forwarded-Proto
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Optional cookies security (enable in prod if you use Django sessions/CSRF)
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# ------------------------------------------------------
# Installed apps
# ------------------------------------------------------
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "drf_spectacular",
    "corsheaders",
    # Project apps
    "api",
    "core.apps.CoreConfig",
]

# ------------------------------------------------------
# Middleware
# (WhiteNoise must be near the top, after SecurityMiddleware)
# ------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # static files in prod
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "greencart.urls"

# ------------------------------------------------------
# Templates
# ------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],  # add template dirs if needed
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "greencart.wsgi.application"

# ------------------------------------------------------
# Database (Render: DATABASE_URL → Postgres; local fallback → SQLite)
# ------------------------------------------------------
DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
        conn_max_age=600,
        ssl_require=not DEBUG,
    )
}

# ------------------------------------------------------
# Password validation
# ------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ------------------------------------------------------
# I18N / TZ
# ------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ------------------------------------------------------
# Static files (WhiteNoise)
# ------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    }
}

# ------------------------------------------------------
# DRF / OpenAPI / JWT
# ------------------------------------------------------
SPECTACULAR_SETTINGS = {
    "TITLE": "GreenCart Logistics API",
    "VERSION": "1.0.0",
}

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    # Lock down by default; loosen per-view if needed
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}

# ------------------------------------------------------
# CORS / CSRF (set these env vars to your Vercel URL)
# e.g. CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
#      CSRF_TRUSTED_ORIGINS=https://your-frontend.vercel.app
# ------------------------------------------------------
CORS_ALLOWED_ORIGINS = env_list("CORS_ALLOWED_ORIGINS=https://pm-dasboard-frontend.vercel.app/", "")
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS=https://pm-dasboard-frontend.vercel.app/", "")
CORS_ALLOW_CREDENTIALS = True

# ------------------------------------------------------
# Default PK
# ------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
