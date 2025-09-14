"""
Django settings for portfolio project.

Simplified for:
- Local development via `python manage.py runserver` (SQLite by default)
- Railway deployment with Docker (DATABASE_URL or MySQL envs)
"""

from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent.parent


def _env_bool(name: str, default: str = "0") -> bool:
    val = os.getenv(name, default)
    return str(val).lower() in ("1", "true", "yes", "on")


SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure-secret-key-change-me")
DEBUG = _env_bool("DEBUG", "1")


# Hosts / CSRF
def _split_csv(value: str) -> list[str]:
    return [v.strip() for v in (value or "").split(",") if v.strip()]

ALLOWED_HOSTS = _split_csv(os.getenv("ALLOWED_HOSTS", ""))
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"] if DEBUG else ["*"]

CSRF_TRUSTED_ORIGINS = _split_csv(os.getenv("CSRF_TRUSTED_ORIGINS", ""))


# Applications
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Local apps
    "core",
    "contact",
    "faq",
    "openapp",
    "analytics",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "portfolio.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(BASE_DIR / "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "analytics.context_processors.analytics",
            ],
        },
    },
]


WSGI_APPLICATION = "portfolio.wsgi.application"


# Database
# Priority: DATABASE_URL -> explicit MySQL envs -> SQLite
DATABASES = {}

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    import dj_database_url

    DATABASES["default"] = dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
    )
else:
    MYSQL_HOST = os.getenv("MYSQL_HOST") or os.getenv("MYSQLHOST")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE") or os.getenv("MYSQLDATABASE")
    MYSQL_USER = os.getenv("MYSQL_USER") or os.getenv("MYSQLUSER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD") or os.getenv("MYSQLPASSWORD")
    MYSQL_PORT = os.getenv("MYSQL_PORT") or os.getenv("MYSQLPORT", "3306")

    if all([MYSQL_HOST, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD]):
        DATABASES["default"] = {
            "ENGINE": "django.db.backends.mysql",
            "NAME": MYSQL_DATABASE,
            "USER": MYSQL_USER,
            "PASSWORD": MYSQL_PASSWORD,
            "HOST": MYSQL_HOST,
            "PORT": MYSQL_PORT,
            "OPTIONS": {
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
                "charset": "utf8mb4",
            },
        }
    else:
        DATABASES["default"] = {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# I18N
LANGUAGE_CODE = "es"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# Static & media
STATIC_URL = "static/"
STATIC_ROOT = str(BASE_DIR / "staticfiles")
STATICFILES_DIRS = [str(BASE_DIR / "static")]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = str(BASE_DIR / "media")


# Security (behind proxy)
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = _env_bool("SECURE_SSL_REDIRECT", "1")


# Analytics (GTM / GA)
GTM_CONTAINER_ID = os.getenv("GTM_CONTAINER_ID", "")
GA_MEASUREMENT_ID = os.getenv("GA_MEASUREMENT_ID", "")

# reCAPTCHA v2 ("No soy un robot")
RECAPTCHA_SITE_KEY = os.getenv("RECAPTCHA_SITE_KEY", "")
RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY", "")
RECAPTCHA_ENABLED = _env_bool("RECAPTCHA_ENABLED", "1")


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
