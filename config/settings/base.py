# config/settings/base.py
import os
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # .../config/..
env = environ.Env(DEBUG=(bool, True))

ENV_FILE = BASE_DIR / '.env'     # /srv/tdp/.env
if ENV_FILE.exists():            # читаем только если файл реально есть
    environ.Env.read_env(str(ENV_FILE))

SECRET_KEY = env('SECRET_KEY', default='unsafe-dev-key')
# Отладочный режим (по умолчанию True для разработки)
DEBUG = env.bool('DEBUG', default=True)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])  # важно для Django 4.2+

# Если ты за Caddy/Nginx — включаем корректную схему https
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Django apps (минимально)
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',  # enable humanize template tags
    # твои приложения:
    'core', 'tours.apps.ToursConfig', 'services', 'reviews', 'prices', 'backup',
    # новые приложения
    'news',
    'blog',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # общая папка шаблонов проекта (если используешь)
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,  # искать шаблоны внутри apps/<app>/templates
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.site_settings",
                "core.context_processors.active_page",
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# БД
DATABASES = {
    'default': env.db(
        'DATABASE_URL',
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
    )
}

# статика/медиа
STATIC_URL = "/static/"
MEDIA_URL = "/media/"
STATIC_ROOT = os.getenv("DJANGO_STATIC_ROOT", BASE_DIR / "static_collected")
MEDIA_ROOT = os.getenv("DJANGO_MEDIA_ROOT", BASE_DIR / "media")
# Папка с общими статическими файлами проекта (CSS, JS, изображения и т.д.)
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
# Используем ManifestStaticFilesStorage для продакшена
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Asia/Bishkek'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Почта по умолчанию SMTP (перекроем в dev)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@example.com')

# Логирование — чтобы видеть 500 в логах контейнера
LOG_LEVEL = env('LOG_LEVEL', default='INFO')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {'format': '[%(levelname)s] %(asctime)s %(name)s: %(message)s'},
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': LOG_LEVEL,
    },
}
