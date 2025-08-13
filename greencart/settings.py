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

def env_list(key: str, default: str = ""):
    raw = os.getenv(key, default)
    return [s.strip() for s in raw.split(",") if s.strip()]

# ------------------------------------------------------
# Core security / debug
# ------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-unsafe-key")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# IMPORTANT: hostnames only, no scheme or slashes
ALLOWED_HOSTS = env_list(
    "ALLOWED_HOSTS",
    "pm-dasboard-backend.onrender.com,localhost,127.0.0.1"
)

# Render proxy -> trust X-Forwarded-Proto
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Cookies hardened in prod
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
# Middleware (WhiteNoise after Security, CORS before Common)
# ------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
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
        "DIRS": [],
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
# Database (Postgres on Render; SQLite locally)
# Avoid passing sslmode to SQLite by detecting scheme
# ------------------------------------------------------
db_url = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'db.sqlite3'}")
ssl_required = db_url.startswith("postgres://") or db_url.startswith("postgresql://")

DATABASES = {
    "default": dj_database_url.parse(
        db_url,
        conn_max_age=600,
        ssl_require=ssl_required,  # only True for Postgres
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
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}

# ------------------------------------------------------
# CORS / CSRF
# Put your Vercel site URL(s) as full origins with scheme.
# e.g. CORS_ALLOWED_ORIGINS="https://pm-dasboard-frontend.vercel.app"
# ------------------------------------------------------
CORS_ALLOWED_ORIGINS = env_list("CORS_ALLOWED_ORIGINS", "")
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS", "")
CORS_ALLOW_CREDENTIALS = True

# ------------------------------------------------------
# Default PK
# ------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
