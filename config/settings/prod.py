# config/settings/prod.py
from .base import *

# Используем переменные окружения для продакшена
DEBUG = env.bool('DEBUG', default=False)
SECRET_KEY = env('SECRET_KEY', default='unsafe-dev-key-change-in-production')

# Домены для продакшена из переменных окружения
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['thaidreamphuket.com', 'www.thaidreamphuket.com'])
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=['https://thaidreamphuket.com', 'https://www.thaidreamphuket.com'])

# cookies по https
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# если весь сайт только по https и у тебя Caddy/Nginx с TLS:
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 год
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Статика и медиа для продакшена из переменных окружения
STATIC_URL = env('STATIC_URL', default='/static/')
STATIC_ROOT = env('STATIC_ROOT', default=BASE_DIR / "staticfiles")
MEDIA_URL = env('MEDIA_URL', default='/media/')
MEDIA_ROOT = env('MEDIA_ROOT', default=BASE_DIR / "media")

# Убираем STATICFILES_DIRS для продакшена, так как статика собирается в STATIC_ROOT
STATICFILES_DIRS = []

# Настройки для раздачи статики в продакшене
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Добавляем whitenoise для раздачи статики в продакшене
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Добавляем whitenoise
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# База данных для продакшена из переменных окружения
DATABASES = {
    'default': env.db(
        'DATABASE_URL',
        default=f"sqlite:///{BASE_DIR / 'data' / 'db.sqlite3'}"
    )
}

# Логирование для продакшена из переменных окружения
LOG_LEVEL = env('LOG_LEVEL', default='INFO')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[%(levelname)s] %(asctime)s %(name)s: %(message)s',
        },
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
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
    },
}
