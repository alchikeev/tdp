#!/bin/bash

# Скрипт для проверки настроек Django в контейнере
# Использование: ./check-settings.sh

echo "🔍 Проверяем настройки Django в контейнере..."

# Проверяем, что мы в правильной директории
if [ ! -f "manage.py" ]; then
    echo "❌ Ошибка: Запустите скрипт из корневой директории проекта"
    exit 1
fi

echo "📊 Информация о базе данных:"
docker compose exec web python manage.py shell -c "
from django.conf import settings
print(f'DATABASE_NAME: {settings.DATABASES[\"default\"][\"NAME\"]}')
print(f'DATABASE_ENGINE: {settings.DATABASES[\"default\"][\"ENGINE\"]}')
print(f'DEBUG: {settings.DEBUG}')
print(f'ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}')
print(f'STATIC_ROOT: {settings.STATIC_ROOT}')
print(f'MEDIA_ROOT: {settings.MEDIA_ROOT}')
print(f'LOG_LEVEL: {settings.LOG_LEVEL}')
"

echo "✅ Проверка завершена!"
