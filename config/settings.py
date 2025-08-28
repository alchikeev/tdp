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

# ===== i18n/time =====
LANGUAGE_CODE = "ru"
TIME_ZONE = "Asia/Bishkek"
USE_I18N = True
USE_TZ = True

# ===== всякая мелочь =====
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
