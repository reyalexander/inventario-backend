from .settings import *
import os
import sys
from pathlib import Path
import environ

# Detectar carpeta real del ejecutable o del proyecto
if getattr(sys, "frozen", False):
    APP_DIR = Path(sys.executable).resolve().parent
else:
    APP_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(DEBUG=(bool, False))

env_file = APP_DIR / ".env.desktop"
if env_file.exists():
    environ.Env.read_env(str(env_file))

DEBUG = False
SECRET_KEY = env("SECRET_KEY", default=SECRET_KEY)

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8001",
    "http://localhost:8001",
]

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

INSTALLED_APPS = [app for app in INSTALLED_APPS if app not in [
    "drf_yasg",
]]

# RUTAS REALES PARA DESKTOP
DATA_DIR = APP_DIR / "data"
MEDIA_DIR = DATA_DIR / "media"
STATICFILES_DIR = APP_DIR / "staticfiles"

DATA_DIR.mkdir(parents=True, exist_ok=True)
MEDIA_DIR.mkdir(parents=True, exist_ok=True)
STATICFILES_DIR.mkdir(parents=True, exist_ok=True)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(DATA_DIR / "db.sqlite3"),
    }
}

STATIC_URL = "/static/"
STATIC_ROOT = str(STATICFILES_DIR)

# Quitar STATICFILES_DIRS para evitar warning de carpeta inexistente
STATICFILES_DIRS = []

MEDIA_URL = "/media/"
MEDIA_ROOT = str(MEDIA_DIR)

REST_FRAMEWORK = REST_FRAMEWORK.copy()
REST_FRAMEWORK["DEFAULT_SCHEMA_CLASS"] = "rest_framework.schemas.openapi.AutoSchema"

SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "SAMEORIGIN"