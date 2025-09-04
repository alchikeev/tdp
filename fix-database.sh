#!/bin/bash

# Скрипт для исправления базы данных на сервере
# Использование: ./fix-database.sh

set -e

echo "🔧 Исправляем базу данных..."

# Проверяем, что мы в правильной директории
if [ ! -f "manage.py" ]; then
    echo "❌ Ошибка: Запустите скрипт из корневой директории проекта"
    exit 1
fi

# Останавливаем контейнер
echo "🛑 Останавливаем контейнер..."
docker compose down

# Удаляем старую базу данных (если есть)
echo "🗑️ Удаляем старую базу данных..."
docker volume rm tdp_data 2>/dev/null || true

# Создаем новую базу данных
echo "📦 Создаем новую базу данных..."
docker volume create tdp_data

# Запускаем контейнер
echo "🐳 Запускаем контейнер..."
docker compose up -d

# Ждем запуска контейнера
echo "⏳ Ждем запуска контейнера..."
sleep 10

# Применяем миграции
echo "🗄️ Применяем миграции..."
docker compose exec web python manage.py migrate --run-syncdb

# Создаем суперпользователя (опционально)
echo "👤 Создаем суперпользователя..."
docker compose exec web python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Суперпользователь создан: admin/admin123')
else:
    print('Суперпользователь уже существует')
"

# Собираем статику
echo "📦 Собираем статические файлы..."
docker compose exec web python manage.py collectstatic --noinput

echo "✅ База данных исправлена!"
echo "🌐 Сайт должен работать по адресу: https://thaidreamphuket.com"
echo "👤 Админка: https://thaidreamphuket.com/admin (admin/admin123)"
