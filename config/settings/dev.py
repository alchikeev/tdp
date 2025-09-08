# config/settings/dev.py
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

INTERNAL_IPS = ['127.0.0.1', 'localhost']

# Для локальной разработки используем пути из base.py
# Статика и медиа раздаются через Django в режиме DEBUG=True
