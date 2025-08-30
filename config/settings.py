# config/settings.py
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

# ===== env =====
env = environ.Env(
    DEBUG=(bool, False),
)
# .env лежит в корне проекта (рядом с manage.py)
environ.Env.read_env(BASE_DIR.parent / ".env")

DEBUG = env("DEBUG", default=True)
SECRET_KEY = env("SECRET_KEY", default="dev-secret-change-me")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["127.0.0.1", "192.168.1.215",  "localhost", "0.0.0.0"])

# ===== приложения =====
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",

    "core",
    "tours",
    "services",
    "reviews",
    "prices",
    "backup",
]

# ===== middleware =====
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # можно оставить даже в DEV
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ===== корневые файлы =====
ROOT_URLCONF = "config.urls"            # <— ЭТО важно, у тебя этого нет
WSGI_APPLICATION = "config.wsgi.application"

# ===== шаблоны =====
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [ BASE_DIR / "templates" ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.site_settings",  # если используется
            ],
        },
    },
]

# ===== база данных =====
# В DEV — sqlite3. На проде можно переопределить через .env (ENGINE/NAME/USER/…)
DATABASES = {
    "default": {
        "ENGINE": env("DB_ENGINE", default="django.db.backends.sqlite3"),
        "NAME": env("DB_NAME", default=str(BASE_DIR / "db.sqlite3")),
        "USER": env("DB_USER", default=""),
        "PASSWORD": env("DB_PASSWORD", default=""),
        "HOST": env("DB_HOST", default=""),
        "PORT": env("DB_PORT", default=""),
    }
}

# ===== статика и медиа =====
STATIC_URL = "/static/"
STATICFILES_DIRS = [ BASE_DIR / "static" ]      # исходники
STATIC_ROOT = BASE_DIR / "staticfiles"          # сборка (collectstatic)
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ----- production / env-driven overrides -----
# ALLOWED_HOSTS из .env (записывайте через запятую)
ALLOWED_HOSTS = [h.strip() for h in env('ALLOWED_HOSTS', default='').split(',') if h.strip()] or ALLOWED_HOSTS

# CSRF_TRUSTED_ORIGINS должны включать схему (https://...)
CSRF_TRUSTED_ORIGINS = [o.strip() for o in env('CSRF_TRUSTED_ORIGINS', default='').split(',') if o.strip()]

# Работа за реверс-прокси (Caddy)
sp = env('SECURE_PROXY_SSL_HEADER', default='')
if sp:
    SECURE_PROXY_SSL_HEADER = tuple(s.strip() for s in sp.split(','))
USE_X_FORWARDED_HOST = True

SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', default=True)
CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', default=True)

# Пути статик/медиа из .env (совпадают с docker-compose)
STATIC_URL = env('STATIC_URL', default=str(STATIC_URL))
MEDIA_URL = env('MEDIA_URL', default=str(MEDIA_URL))
STATIC_ROOT = env('STATIC_ROOT', default=str(STATIC_ROOT))
MEDIA_ROOT = env('MEDIA_ROOT', default=str(MEDIA_ROOT))

# ===== i18n/time =====
LANGUAGE_CODE = "ru"
TIME_ZONE = "Asia/Bishkek"
USE_I18N = True
USE_TZ = True

# ===== всякая мелочь =====
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
