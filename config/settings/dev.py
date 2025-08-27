from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']   # локалка/стенд

# Для dev можно почту слать в консоль
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
