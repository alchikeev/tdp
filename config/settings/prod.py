# config/settings/prod.py
from .base import *

DEBUG = False

# Домены для продакшена
ALLOWED_HOSTS = ["thaidreamphuket.com", "www.thaidreamphuket.com"]
CSRF_TRUSTED_ORIGINS = ["https://thaidreamphuket.com", "https://www.thaidreamphuket.com"]

# cookies по https
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# если весь сайт только по https и у тебя Caddy/Nginx с TLS:
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 год
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Статика и медиа для продакшена
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

# База данных для продакшена (SQLite в контейнере)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'data' / 'db.sqlite3',
    }
}

# Логирование для продакшена
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
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
