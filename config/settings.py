import os
from pathlib import Path
import environ

# ==== БАЗА ПУТЕЙ ====
BASE_DIR = Path(__file__).resolve().parent.parent  # .../TravelWorld/TravelWorld

# ==== ENV ====
# .env лежит рядом с manage.py: .../TravelWorld/.env
env = environ.Env(
    DEBUG=(bool, False),
)
environ.Env.read_env(BASE_DIR.parent / '.env')

# ==== БЕЗОПАСНОСТЬ ====
SECRET_KEY = env('SECRET_KEY', default='dev-please-change-me')
DEBUG = env.bool('DEBUG', default=True)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])

# ==== ПРИЛОЖЕНИЯ ====
INSTALLED_APPS = [
    'core',
    'tours',
    'services',
    'django.contrib.admin',
    'django.contrib.humanize',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# ==== MIDDLEWARE ====
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

# ==== ШАБЛОНЫ ====
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ BASE_DIR / 'templates' ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ==== БАЗА ДАННЫХ ====
# Использует DATABASE_URL из .env если задан, иначе sqlite по умолчанию
DATABASES = {
    'default': env.db(default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")
}

# ==== ПАРОЛИ ====
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ==== ЛОКАЛИ И ВРЕМЯ ====
LANGUAGE_CODE = 'ru'               # интерфейс по умолчанию — русский
TIME_ZONE = 'Asia/Bangkok'         # Пхукет / Таиланд
USE_I18N = True
USE_TZ = True                      # хранить в UTC, показывать по TIME_ZONE

# ==== СТАТИКА / МЕДИА ====
STATIC_URL = '/static/'
STATICFILES_DIRS = [ BASE_DIR / 'static' ]  # исходники
STATIC_ROOT = BASE_DIR / 'staticfiles'      # сюда соберёт collectstatic

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ==== ПРОЧЕЕ ====
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
