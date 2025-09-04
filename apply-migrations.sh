#!/bin/bash

# Скрипт для применения непримененных миграций
# Использование: ./apply-migrations.sh

set -e

echo "🔄 Применяем непримененные миграции..."

# Проверяем, что мы в правильной директории
if [ ! -f "manage.py" ]; then
    echo "❌ Ошибка: Запустите скрипт из корневой директории проекта"
    exit 1
fi

# Показываем статус миграций
echo "📊 Текущий статус миграций:"
docker compose exec web python manage.py showmigrations

echo ""
echo "🗄️ Применяем все миграции..."
docker compose exec web python manage.py migrate

echo "📊 Статус миграций после применения:"
docker compose exec web python manage.py showmigrations

echo "✅ Миграции применены!"
echo "🌐 Проверьте сайт: https://thaidreamphuket.com"
