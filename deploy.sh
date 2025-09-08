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

# Инициализируем структуру папок
echo "📁 Инициализируем структуру папок..."

# Создаем папку для статических файлов
if [ ! -d "/srv/tdp-static" ]; then
    echo "🔧 Создаем папку для статических файлов..."
    sudo mkdir -p /srv/tdp-static
    echo "✅ Папка /srv/tdp-static создана"
else
    echo "✅ Папка /srv/tdp-static уже существует"
fi

# Создаем папку для данных
if [ ! -d "/srv/tdp-data" ]; then
    echo "🔧 Создаем структуру папок для данных..."
    sudo mkdir -p /srv/tdp-data/{media,data}
    echo "✅ Структура папок /srv/tdp-data создана"
else
    echo "✅ Структура папок /srv/tdp-data уже существует"
    # Убеждаемся, что все подпапки существуют
    sudo mkdir -p /srv/tdp-data/media
    sudo mkdir -p /srv/tdp-data/data
fi

# Проверяем права доступа
echo "🔧 Проверяем права доступа..."
sudo chown -R 1000:1000 /srv/tdp-static
sudo chown -R 1000:1000 /srv/tdp-data
sudo chmod -R 755 /srv/tdp-static
sudo chmod -R 755 /srv/tdp-data

# Проверяем, что папки созданы и доступны
if [ ! -d "/srv/tdp-static" ] || [ ! -d "/srv/tdp-data/media" ] || [ ! -d "/srv/tdp-data/data" ]; then
    echo "❌ Ошибка: Не удалось создать все необходимые папки"
    exit 1
fi

echo "✅ Все папки созданы и настроены правильно"

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

# Проверяем, существует ли база данных
echo "🔍 Проверяем наличие базы данных..."
if [ ! -f "/srv/tdp-data/data/db.sqlite3" ]; then
    echo "📝 База данных не найдена, создаем новую..."
    # Создаем пустую базу данных
    docker compose run --rm -e DJANGO_SETTINGS_MODULE=config.settings.prod tdp-web python manage.py migrate --run-syncdb
else
    echo "✅ База данных найдена, применяем миграции..."
    docker compose run --rm -e DJANGO_SETTINGS_MODULE=config.settings.prod tdp-web python manage.py migrate
fi

# Собираем статику
echo "📦 Собираем статические файлы..."
docker compose run --rm -e DJANGO_SETTINGS_MODULE=config.settings.prod tdp-web python manage.py collectstatic --noinput

# Проверяем, что база данных создалась успешно
echo "🔍 Проверяем создание базы данных..."
if [ -f "/srv/tdp-data/data/db.sqlite3" ] && [ -s "/srv/tdp-data/data/db.sqlite3" ]; then
    echo "✅ База данных создана успешно"
    
    # Проверяем, есть ли таблицы в базе данных
    TABLE_COUNT=$(docker compose run --rm -e DJANGO_SETTINGS_MODULE=config.settings.prod tdp-web python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.prod')
import django
django.setup()
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table';\")
    tables = cursor.fetchall()
    print(len(tables))
" 2>/dev/null || echo "0")
    
    if [ "$TABLE_COUNT" -gt 0 ]; then
        echo "✅ В базе данных найдено $TABLE_COUNT таблиц"
    else
        echo "⚠️  База данных пуста, рекомендуется создать суперпользователя:"
        echo "   docker compose run --rm -e DJANGO_SETTINGS_MODULE=config.settings.prod tdp-web python manage.py createsuperuser"
    fi
else
    echo "❌ Ошибка: База данных не была создана"
    exit 1
fi

# Запускаем контейнер
echo "🐳 Запускаем контейнер..."
docker compose up -d

# Проверяем, что запустились контейнеры
echo "📊 Проверяем запущенные контейнеры..."
WEB_CONTAINER_COUNT=$(docker ps --filter "name=tdp-web" --format "{{.Names}}" | wc -l)
CADDY_CONTAINER_COUNT=$(docker ps --filter "name=tdp-caddy" --format "{{.Names}}" | wc -l)

if [ "$WEB_CONTAINER_COUNT" -eq 1 ] && [ "$CADDY_CONTAINER_COUNT" -eq 1 ]; then
    echo "✅ Запущены контейнеры:"
    docker ps --filter "name=tdp" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
else
    echo "⚠️  Внимание: Запущено $WEB_CONTAINER_COUNT web контейнеров и $CADDY_CONTAINER_COUNT caddy контейнеров"
    docker ps --filter "name=tdp" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
fi

# Очищаем старые образы
echo "🧹 Очищаем старые образы..."
docker image prune -f

echo "✅ Деплой завершен!"
echo "🌐 Приложение доступно по адресу: https://thaidreamphuket.com"
echo "📊 Проверить статус: docker compose ps"
echo "📋 Логи: docker compose logs -f tdp-web"
