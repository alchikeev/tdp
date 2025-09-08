#!/bin/bash
set -e

# Создаем директории для статики и медиа из переменных окружения
STATIC_ROOT=${DJANGO_STATIC_ROOT:-/app/static_collected}
MEDIA_ROOT=${DJANGO_MEDIA_ROOT:-/app/media}

echo "Creating directories: $STATIC_ROOT, $MEDIA_ROOT"
mkdir -p "$STATIC_ROOT" "$MEDIA_ROOT"

# Устанавливаем права на директории
echo "Setting ownership to appuser:appuser"
chown -R appuser:appuser "$STATIC_ROOT" "$MEDIA_ROOT"

# Выполняем миграции
echo "Running migrations..."
python manage.py migrate --noinput

# Собираем статику
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Запускаем gunicorn
echo "Starting gunicorn..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --keep-alive 5 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --access-logfile - \
    --error-logfile -
