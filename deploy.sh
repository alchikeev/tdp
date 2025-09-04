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

# Устанавливаем правильные права доступа для volumes
echo "🔧 Устанавливаем права доступа для volumes..."
docker run --rm -v tdp_static_data:/data alpine chown -R 1000:1000 /data
docker run --rm -v tdp_media_data:/data alpine chown -R 1000:1000 /data
docker run --rm -v tdp_data:/data alpine chown -R 1000:1000 /data

# Очищаем кэш Docker Compose и удаляем override файлы
echo "🧹 Очищаем кэш Docker Compose..."
docker compose config > /dev/null 2>&1 || true

# Удаляем возможные override файлы
echo "🧹 Удаляем override файлы..."
rm -f docker-compose.override.yml 2>/dev/null || true
rm -f .docker-compose.override.yml 2>/dev/null || true

# Очищаем кэш Docker Compose полностью
echo "🧹 Очищаем кэш Docker Compose полностью..."
docker compose down --remove-orphans 2>/dev/null || true

# Собираем новый образ
echo "🔨 Собираем Docker образ..."
docker compose build --no-cache

# Проверяем конфигурацию и доступные сервисы
echo "📋 Проверяем конфигурацию Docker Compose..."
docker compose config --services

# Применяем миграции
echo "🗄️ Применяем миграции базы данных..."
docker compose run --rm -e DJANGO_SETTINGS_MODULE=config.settings.prod tdp-web python manage.py migrate

# Собираем статику
echo "📦 Собираем статические файлы..."
docker compose run --rm -e DJANGO_SETTINGS_MODULE=config.settings.prod tdp-web python manage.py collectstatic --noinput

# Запускаем контейнер
echo "🐳 Запускаем контейнер..."
docker compose up -d

# Проверяем, что запустился контейнер
echo "📊 Проверяем запущенные контейнеры..."
CONTAINER_COUNT=$(docker ps --filter "name=tdp-web" --format "{{.Names}}" | wc -l)
if [ "$CONTAINER_COUNT" -eq 1 ]; then
    echo "✅ Запущен контейнер:"
    docker ps --filter "name=tdp-web" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
else
    echo "⚠️  Внимание: Запущено $CONTAINER_COUNT контейнеров с именем tdp-web (ожидается 1)"
    docker ps --filter "name=tdp" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
fi

# Очищаем старые образы
echo "🧹 Очищаем старые образы..."
docker image prune -f

echo "✅ Деплой завершен!"
echo "🌐 Приложение доступно по адресу: https://thaidreamphuket.com"
echo "📊 Проверить статус: docker compose ps"
echo "📋 Логи: docker compose logs -f tdp-web"
