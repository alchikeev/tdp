import os
from pathlib import Path
import environ

# Загружаем переменные окружения и выбираем модуль настроек из .env
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
env.read_env(BASE_DIR / '.env')
os.environ.setdefault(
	'DJANGO_SETTINGS_MODULE',
	env('DJANGO_SETTINGS_MODULE', default='config.settings.dev')
)

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()