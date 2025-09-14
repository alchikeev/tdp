#!/usr/bin/env bash
set -e

PROJECT_DIR="/srv/tdp"
COMPOSE_FILE="docker-compose.prod.yml"
SERVICE_NAME="tdp-web"

echo "➡️  Переходим в $PROJECT_DIR"
cd $PROJECT_DIR

echo "➡️  Чистим старые хвосты..."
docker ps -a --filter "name=tdp-tdp-web" --format "{{.ID}}" | xargs -r docker rm -f

echo "➡️  Обновляем репозиторий..."
git pull origin main

echo "➡️  Пересобираем контейнеры..."
docker compose -f $COMPOSE_FILE build --no-cache

echo "➡️  Запускаем контейнеры..."
docker compose -f $COMPOSE_FILE up -d

echo "➡️  Применяем миграции..."
docker compose -f $COMPOSE_FILE run --rm $SERVICE_NAME python manage.py migrate --noinput

echo "➡️  Собираем статику..."
docker compose -f $COMPOSE_FILE run --rm $SERVICE_NAME python manage.py collectstatic --noinput

echo "✅ Деплой завершён!"
