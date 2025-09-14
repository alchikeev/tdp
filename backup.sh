#!/bin/bash

# Скрипт резервного копирования TDP
# Создает архив с базой данных и медиа файлами
# Автоматически определяет пути из настроек Django

set -e  # Остановить выполнение при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Проверяем, что мы находимся в корневой директории проекта
if [ ! -f "manage.py" ]; then
    error "Скрипт должен быть запущен из корневой директории Django проекта"
    exit 1
fi

# Определяем директорию для сохранения бэкапа
# По умолчанию - папка Загрузки пользователя
if [ -d "$HOME/Downloads" ]; then
    BACKUP_DIR="$HOME/Downloads"
elif [ -d "$HOME/Desktop" ]; then
    BACKUP_DIR="$HOME/Desktop"
else
    BACKUP_DIR="."
fi

# Генерируем имя файла с датой и временем
TIMESTAMP=$(date +"%d%m%Y_%H%M%S")
BACKUP_NAME="tdp_${TIMESTAMP}.zip"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"

log "Начинаем создание резервной копии..."
log "Файл будет сохранен в: $BACKUP_PATH"

# Определяем пути к базе данных и медиа файлам
log "Определяем пути к данным..."

# Получаем путь к базе данных из manage.py
DB_PATH=$(python -c "
import os
import sys
import django
sys.path.append('.')
# Определяем настройки автоматически
if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
try:
    django.setup()
    from django.conf import settings
    print(settings.DATABASES['default']['NAME'])
except Exception as e:
    # Fallback к стандартным путям
    print('db.sqlite3')
" 2>/dev/null)

# Получаем путь к медиа файлам
MEDIA_PATH=$(python -c "
import os
import sys
import django
sys.path.append('.')
# Определяем настройки автоматически
if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
try:
    django.setup()
    from django.conf import settings
    print(settings.MEDIA_ROOT)
except Exception as e:
    # Fallback к стандартным путям
    print('media')
" 2>/dev/null)

# Если пути не определены, используем стандартные
if [ -z "$DB_PATH" ]; then
    DB_PATH="db.sqlite3"
fi

if [ -z "$MEDIA_PATH" ]; then
    MEDIA_PATH="media"
fi

log "База данных: $DB_PATH"
log "Медиа файлы: $MEDIA_PATH"

# Проверяем наличие базы данных
if [ ! -f "$DB_PATH" ]; then
    error "База данных не найдена: $DB_PATH"
    exit 1
fi

# Проверяем наличие медиа файлов
if [ ! -d "$MEDIA_PATH" ]; then
    warning "Директория медиа файлов не найдена: $MEDIA_PATH"
    warning "Создаем пустую директорию"
    mkdir -p "$MEDIA_PATH"
fi

# Создаем временную директорию для архивации
TEMP_DIR=$(mktemp -d)
log "Временная директория: $TEMP_DIR"

# Копируем базу данных
log "Копируем базу данных..."
cp "$DB_PATH" "$TEMP_DIR/db.sqlite3"

# Копируем медиа файлы
log "Копируем медиа файлы..."
cp -r "$MEDIA_PATH" "$TEMP_DIR/media"

# Создаем файл с информацией о бэкапе
cat > "$TEMP_DIR/backup_info.txt" << EOF
TDP Backup Information
=====================
Created: $(date)
Database: $DB_PATH
Media: $MEDIA_PATH
Backup script: backup.sh
Django version: $(python manage.py --version 2>/dev/null || echo "Unknown")
Django settings: ${DJANGO_SETTINGS_MODULE:-config.settings.dev}
EOF

# Создаем архив
log "Создаем архив $BACKUP_NAME..."
cd "$TEMP_DIR"
zip -r "temp_backup.zip" . > /dev/null 2>&1
ZIP_EXIT_CODE=$?
cd - > /dev/null

if [ $ZIP_EXIT_CODE -eq 0 ]; then
    mv "$TEMP_DIR/temp_backup.zip" "$BACKUP_PATH"
    log "Архив создан успешно"
else
    error "Ошибка при создании архива (код: $ZIP_EXIT_CODE)"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# Очищаем временную директорию
rm -rf "$TEMP_DIR"

# Проверяем размер архива
ARCHIVE_SIZE=$(du -h "$BACKUP_PATH" | cut -f1)
log "Размер архива: $ARCHIVE_SIZE"

# Проверяем, что архив создался успешно
if [ -f "$BACKUP_PATH" ]; then
    success "Резервная копия создана успешно: $BACKUP_PATH"
    
    # Показываем содержимое архива
    log "Содержимое архива:"
    unzip -l "$BACKUP_PATH" | head -20
    
    # Показываем информацию о файле
    echo ""
    log "Архив сохранен локально на вашем компьютере"
    log "Полный путь: $BACKUP_PATH"
    
else
    error "Ошибка при создании архива!"
    exit 1
fi

# Показываем информацию о созданных бэкапах
echo ""
log "Для просмотра всех резервных копий TDP в папке $BACKUP_DIR выполните:"
echo "  ls -la $BACKUP_DIR/tdp_*.zip"

success "Резервное копирование завершено!"