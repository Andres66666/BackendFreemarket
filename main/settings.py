import os
from pathlib import Path
from datetime import timedelta
import cloudinary


BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = "django-insecure-kw5d5g509&zw(cn14nwvrwa$-$uh&)i9j^w#hajmu_wi1udj5m"
DEBUG = True

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "freemarkett.netlify.app",
    "backendfreemarket.onrender.com",
    
]


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "cloudinary",
    "rest_framework",
    "corsheaders",
    "rest_framework_simplejwt",
    "users",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "main.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "main.wsgi.application"

""" DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "Freemarket",
        "USER": "postgres",
        "PASSWORD": "13247291",
        "HOST": "localhost",
        "PORT": "5432",
    }
} """
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "freemarket_ehrq",
        "USER": "freemarket_ehrq_user",
        "PASSWORD": "iu2dNGTkOeMSWZkGViJqBTlQnjDgzu6V",
        "HOST": "dpg-d7ts4e0sfn5c73ce84l0-a.oregon-postgres.render.com",
        "PORT": "5432",
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "es-es"  # Cambiado a español
TIME_ZONE = "America/Lima"  # Ajusta según tu zona horaria
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

# Configuración de Cloudinary (asegúrate que usa variables de entorno)
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.getenv("dz45dhxii"),
    "API_KEY": os.getenv("419624749789857"),
    "API_SECRET": os.getenv("lOJH1C6pH2HT9IaeMn89fhVF3Vk"),
    "SECURE": True,
}
cloudinary.config(
    cloud_name="dz45dhxii",
    api_key="419624749789857",
    api_secret="lOJH1C6pH2HT9IaeMn89fhVF3Vk",
)

CLOUDINARY_URL = "cloudinary://API_KEY:API_SECRET@CLOUD_NAME"

# REST Framework
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# JWT Settings
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
}


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
CORS_ALLOW_ALL_ORIGINS = False  # Más seguro que True en producción
CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
    "https://freemarkett.netlify.app",
    "https://backendfreemarket.onrender.com",
]

CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS.copy()
CORS_ALLOW_CREDENTIALS = True

# Configuraciones de seguridad para producción
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Auto primary key
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
