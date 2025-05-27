# Ejercicio/settings.py
# ===========================================================================
#  Django settings para el proyecto «Ejercicio»
#  Funciona igual en local y en Render (se usa SQLite por defecto + MySQL
#  remoto con el alias “mysql_remoto” que emplea vista.py)
# ===========================================================================

from pathlib import Path
import os

# ---------------------------------------------------------------------------
#  Rutas básicas
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
#  Seguridad
# ---------------------------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "clave-segura-de-respaldo")
DEBUG      = os.getenv("DEBUG", "False") == "True"
ALLOWED_HOSTS = ["*"]            # Render inyecta la URL pública aquí

# ---------------------------------------------------------------------------
#  Archivos estáticos
# ---------------------------------------------------------------------------
STATIC_URL  = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"          # para collectstatic

# Recursos que tú mismo subes al repo
STATICFILES_DIRS = [
    BASE_DIR / "Ejercicio" / "web" / "static",
]

# ---------------------------------------------------------------------------
#  Plantillas
# ---------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "Ejercicio" / "web"],   # *.html sueltos
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

# ---------------------------------------------------------------------------
#  Aplicaciones y middleware
# ---------------------------------------------------------------------------
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
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF   = "Ejercicio.urls"
WSGI_APPLICATION = "Ejercicio.wsgi.application"

# ---------------------------------------------------------------------------
#  Bases de datos
# ---------------------------------------------------------------------------
#
#  • “default” → SQLite para tablas internas de Django.
#  • “mysql_remoto” → tu servidor MySQL; es el alias que usa vista.py.
#
import pymysql, django.db.backends.mysql.base as mysql_base
pymysql.install_as_MySQLdb()

# Truco para que Django-5.2 no falle si el servidor devuelve versión 8.0.11
mysql_base.DatabaseWrapper.get_database_version = lambda self: (8, 0, 11)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
    "mysql_remoto": {
        "ENGINE":  "django.db.backends.mysql",
        "NAME":    os.getenv("DB_NAME",     "compilador25z19"),
        "USER":    os.getenv("DB_USER",     "usr_comp25z19_oper"),
        "PASSWORD":os.getenv("DB_PASSWORD", "[qRnCTk$:W>r"),
        "HOST":    os.getenv("DB_HOST",     "www.server.daossystem.pro"),
        "PORT":    os.getenv("DB_PORT",     "3301"),
        "OPTIONS": {"sql_mode": "STRICT_TRANS_TABLES"},
    },
}

# ---------------------------------------------------------------------------
#  Passwords, i18n, etc.
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
#  SMTP (opcional)
# ---------------------------------------------------------------------------
EMAIL_BACKEND       = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST          = "smtp.gmail.com"
EMAIL_PORT          = 587
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = os.getenv("EMAIL_HOST_USER", "javaprueba10@gmail.com")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "qcdkusb fzqqefvtv")
DEFAULT_FROM_EMAIL  = EMAIL_HOST_USER
