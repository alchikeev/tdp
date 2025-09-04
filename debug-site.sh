#!/bin/bash

# Скрипт для диагностики проблем с сайтом
# Использование: ./debug-site.sh

set -e

echo "🔍 Диагностика проблем с сайтом..."

# Проверяем, что мы в правильной директории
if [ ! -f "manage.py" ]; then
    echo "❌ Ошибка: Запустите скрипт из корневой директории проекта"
    exit 1
fi

echo "📊 Проверяем статус контейнера..."
docker compose ps

echo ""
echo "🔍 Проверяем health endpoint..."
curl -I http://localhost:8000/health/ || echo "❌ Health endpoint недоступен"

echo ""
echo "🔍 Проверяем главную страницу..."
curl -I http://localhost:8000/ || echo "❌ Главная страница недоступна"

echo ""
echo "📋 Проверяем логи Django..."
docker compose logs --tail 20 web

echo ""
echo "🗄️ Проверяем миграции..."
docker compose exec web python manage.py showmigrations | grep -E "\[ \]"

echo ""
echo "🔍 Проверяем настройки Django..."
docker compose exec web python manage.py shell -c "
from django.conf import settings
print(f'DEBUG: {settings.DEBUG}')
print(f'ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}')
print(f'DATABASE_NAME: {settings.DATABASES[\"default\"][\"NAME\"]}')
print(f'STATIC_ROOT: {settings.STATIC_ROOT}')
print(f'MEDIA_ROOT: {settings.MEDIA_ROOT}')
"

echo ""
echo "🌐 Проверяем доступность сайта через Caddy..."
curl -I -H "Host: thaidreamphuket.com" http://localhost:8000/ || echo "❌ Сайт недоступен через Caddy"

echo "✅ Диагностика завершена!"
