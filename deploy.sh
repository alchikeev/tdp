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
echo "📊 Текущая ветка: $(git branch --show-current)"
echo "📊 Последний коммит: $(git log -1 --oneline)"
git reset --hard origin/main
echo "📊 Обновлено до: $(git log -1 --oneline)"

# Останавливаем старый контейнер
echo "🛑 Останавливаем старый контейнер..."
docker compose down --remove-orphans

# Удаляем все контейнеры проекта tdp (на всякий случай)
echo "🧹 Удаляем все контейнеры проекта tdp..."
docker container prune -f
docker ps -a --filter "name=tdp" --format "{{.Names}}" | xargs -r docker rm -f

# Удаляем старые volumes и создаем новые (исправляем права доступа)
echo "🧹 Удаляем старые volumes и создаем новые..."
docker volume rm tdp_static_data 2>/dev/null || true
docker volume rm tdp_media_data 2>/dev/null || true
docker volume rm tdp_data 2>/dev/null || true

echo "📦 Создаем необходимые volumes..."
docker volume create tdp_static_data
docker volume create tdp_media_data
docker volume create tdp_data

# Собираем новый образ
echo "🔨 Собираем Docker образ..."
docker compose build --no-cache

# Применяем миграции
echo "🗄️ Применяем миграции базы данных..."
docker compose run --rm -e DJANGO_SETTINGS_MODULE=config.settings.prod web python manage.py migrate

# Собираем статику
echo "📦 Собираем статические файлы..."
docker compose run --rm -e DJANGO_SETTINGS_MODULE=config.settings.prod web python manage.py collectstatic --noinput

# Запускаем контейнер
echo "🐳 Запускаем контейнер..."
docker compose up -d

# Проверяем, что запустился только один контейнер
echo "📊 Проверяем запущенные контейнеры..."
CONTAINER_COUNT=$(docker ps --filter "name=tdp" --format "{{.Names}}" | wc -l)
if [ "$CONTAINER_COUNT" -gt 1 ]; then
    echo "⚠️  Внимание: Запущено $CONTAINER_COUNT контейнеров с именем tdp"
    docker ps --filter "name=tdp" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
else
    echo "✅ Запущен 1 контейнер: $(docker ps --filter "name=tdp" --format "{{.Names}}")"
fi

# Очищаем старые образы
echo "🧹 Очищаем старые образы..."
docker image prune -f

echo "✅ Деплой завершен!"
echo "🌐 Приложение доступно по адресу: https://thaidreamphuket.com"
echo "📊 Проверить статус: docker compose ps"
echo "📋 Логи: docker compose logs -f web"
