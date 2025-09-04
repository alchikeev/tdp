#!/bin/bash

# Скрипт для выполнения команд Django с правильными переменными окружения
# Использование: ./django-shell.sh "команда"

if [ -z "$1" ]; then
    echo "❌ Ошибка: Укажите команду Django"
    echo "Пример: ./django-shell.sh \"from django.conf import settings; print(settings.DATABASES['default']['NAME'])\""
    exit 1
fi

# Проверяем, что мы в правильной директории
if [ ! -f "manage.py" ]; then
    echo "❌ Ошибка: Запустите скрипт из корневой директории проекта"
    exit 1
fi

echo "🐍 Выполняем команду Django: $1"
docker compose exec web python manage.py shell -c "$1"
