#!/bin/bash

# Скрипт для деплоя на VPS
# Использование: ./deploy.sh

set -e

echo "🚀 Начинаем деплой TDP на VPS..."

# Проверяем, что мы в правильной директории
if [ ! -f "manage.py" ]; then
    echo "❌ Ошибка: Запустите скрипт из корневой директории проекта"
    exit 1
fi

# Получаем последнюю версию из GitHub
echo "📥 Получаем последнюю версию из GitHub..."
git fetch origin
git reset --hard origin/main

# Останавливаем старый контейнер
echo "🛑 Останавливаем старый контейнер..."
docker compose down

# Создаем необходимые volumes
echo "📦 Создаем необходимые volumes..."
docker volume create tdp_static_data 2>/dev/null || true
docker volume create tdp_media_data 2>/dev/null || true
docker volume create tdp_data 2>/dev/null || true

# Собираем новый образ
echo "🔨 Собираем Docker образ..."
docker compose build --no-cache

# Инициализируем базу данных
echo "🗄️ Инициализируем базу данных..."
docker compose run --rm web python manage.py migrate --run-syncdb

# Собираем статику
echo "📦 Собираем статические файлы..."
docker compose run --rm web python manage.py collectstatic --noinput

# Запускаем контейнер
echo "🐳 Запускаем контейнер..."
docker compose up -d

# Очищаем старые образы
echo "🧹 Очищаем старые образы..."
docker image prune -f

echo "✅ Деплой завершен!"
echo "🌐 Приложение доступно по адресу: https://thaidreamphuket.com"
echo "📊 Проверить статус: docker-compose ps"
echo "📋 Логи: docker-compose logs -f web"
