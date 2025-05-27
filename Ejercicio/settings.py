# Ejercicio/settings.py
# ===========================================================================
#  Django settings para «Ejercicio»
#  • Sirve los estáticos con WhiteNoise (CSS, JS, imágenes)
#  • Usa la BD remota MySQL 5.7 mediante alias “mysql_remoto”
# ===========================================================================

from pathlib import Path
import os
import pymysql
import django.db.backends.mysql.base as mysql_base

# ─── Rutas base ──────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ─── Seguridad ──────────────────────────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "clave-segura-de-respaldo")
DEBUG      = os.getenv("DEBUG", "False") == "True"
ALLOWED_HOSTS = ["*"]        # Render inyecta su dominio aquí

# ─── Archivos estáticos ─────────────────────────────────────────────────────
STATIC_URL  = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"       # destino de collectstatic
STATICFILES_DIRS = [BASE_DIR / "static"]     # carpeta con tu CSS/JS/img

# WhiteNoise: compresión + hash ▶ evita conflictos de cache
STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
)

# ─── Apps & Middleware ──────────────────────────────────────────────────────
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",        # ↖️ sirve estáticos
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF      = "Ejercicio.urls"
WSGI_APPLICATION  = "Ejercicio.wsgi.application"

# ─── Templates ──────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "Ejercicio" / "web"],        # *.html sueltos
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

# ─── Bases de datos ─────────────────────────────────────────────────────────
#
#  default        → se apunta a la misma MySQL (podrías dejarla SQLite
#                    si quieres; simplemente clónala para simplificar).
#  mysql_remoto   → alias que usa tu código en vista.py
#
pymysql.install_as_MySQLdb()

# ► Hack para que Django-5.2 no exija 8.0.11
mysql_base.DatabaseWrapper.get_database_version = lambda self: (8, 0, 11)

DB_SETTINGS = {
    "ENGINE":   "django.db.backends.mysql",
    "NAME":     os.getenv("DB_NAME",     "compilador25z19"),
    "USER":     os.getenv("DB_USER",     "usr_comp25z19_oper"),
    "PASSWORD": os.getenv("DB_PASSWORD", "[qRnCTk$:W>r"),
    "HOST":     os.getenv("DB_HOST",     "www.server.daossystem.pro"),
    "PORT":     os.getenv("DB_PORT",     "3301"),
    "OPTIONS":  {"sql_mode": "STRICT_TRANS_TABLES"},
}

DATABASES = {
    "default":      DB_SETTINGS,     # usa la misma conexión
    "mysql_remoto": DB_SETTINGS,     # alias adicional
}

# ─── Passwords, i18n, etc. ─────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es"
TIME_ZONE     = "America/Guatemala"
USE_I18N = True
USE_TZ   = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ─── SMTP (opcional) ────────────────────────────────────────────────────────
EMAIL_BACKEND       = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST          = "smtp.gmail.com"
EMAIL_PORT          = 587
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = os.getenv("EMAIL_HOST_USER", "javaprueba10@gmail.com")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "qcdkusbfzqqefvtv")
DEFAULT_FROM_EMAIL  = EMAIL_HOST_USER
