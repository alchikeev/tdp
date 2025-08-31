# config/settings/prod.py
from .base import *

DEBUG = False

# cookies по https
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# если весь сайт только по https и у тебя Caddy/Nginx с TLS:
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 год
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# В проде домены только из .env
