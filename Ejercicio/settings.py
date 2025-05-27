import os
from pathlib import Path
import pymysql

pymysql.install_as_MySQLdb()

# ─── Rutas base ───────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ─── Seguridad ───────────────────────────────────────────────────────────────
SECRET_KEY    = os.environ.get("SECRET_KEY", "clave-segura-de-respaldo")
DEBUG         = os.environ.get("DEBUG", "False") == "True"
ALLOWED_HOSTS = ["*"]                       # cámbialo en producción

# ─── Archivos estáticos ──────────────────────────────────────────────────────
STATIC_URL  = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"      # destino de collectstatic
STATICFILES_DIRS = [BASE_DIR / "static"]    # carpeta fuente (CSS, JS, img)

STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
)

# ─── Aplicaciones ────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

# ─── Middleware ──────────────────────────────────────────────────────────────
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",   # sirve estáticos en prod.
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ─── Enrutamiento ────────────────────────────────────────────────────────────
ROOT_URLCONF = "Ejercicio.urls"

# ─── Plantillas ──────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "Ejercicio" / "web"],   # tus .html
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

# ─── WSGI ─────────────────────────────────────────────────────────────────────
WSGI_APPLICATION = "Ejercicio.wsgi.application"

# ─── Bases de datos ──────────────────────────────────────────────────────────
# ① “default” (por si algo de Django lo necesita)
# ② Alias “mysql_remoto” → el que usa tu código
DB_SETTINGS = {
    "ENGINE": "django.db.backends.mysql",
    "NAME":     os.environ.get("DB_NAME",     ""),
    "USER":     os.environ.get("DB_USER",     ""),
    "PASSWORD": os.environ.get("DB_PASSWORD", ""),
    "HOST":     os.environ.get("DB_HOST",     ""),
    "PORT":     os.environ.get("DB_PORT", "3306"),
    "OPTIONS":  {"sql_mode": "STRICT_TRANS_TABLES"},
}

DATABASES = {
    "default":      DB_SETTINGS,
    "mysql_remoto": DB_SETTINGS,   # ← alias extra
}

# ─── Validadores de contraseña ───────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ─── Internacionalización ────────────────────────────────────────────────────
LANGUAGE_CODE = "es"
TIME_ZONE     = "America/Guatemala"
USE_I18N      = True
USE_TZ        = True

# ─── Clave primaria por defecto ──────────────────────────────────────────────
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ─── Correo SMTP ─────────────────────────────────────────────────────────────
EMAIL_BACKEND       = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST          = "smtp.gmail.com"
EMAIL_PORT          = 587
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = os.environ.get("EMAIL_HOST_USER", "javaprueba10@gmail.com")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "qcdkusbfzqqefvtv")
DEFAULT_FROM_EMAIL  = EMAIL_HOST_USER
