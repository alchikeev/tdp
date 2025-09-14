#!/bin/bash

# Скрипт восстановления TDP
# Восстанавливает базу данных и медиа файлы из архива
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

# Функция показа справки
show_help() {
    echo "Использование: $0 [ОПЦИИ] [АРХИВ]"
    echo ""
    echo "Восстанавливает базу данных и медиа файлы из архива TDP"
    echo ""
    echo "Аргументы:"
    echo "  АРХИВ    Путь к архиву для восстановления (опционально)"
    echo "           Если не указан, скрипт предложит выбрать из найденных"
    echo ""
    echo "Опции:"
    echo "  -h, --help     Показать эту справку"
    echo "  -f, --force    Принудительное восстановление без подтверждения"
    echo "  -d, --dry-run  Показать что будет восстановлено без выполнения"
    echo ""
    echo "Примеры:"
    echo "  $0                                    # Интерактивный выбор архива"
    echo "  $0 tdp_14092025_104500.zip           # Указать архив напрямую"
    echo "  $0 ~/Downloads/tdp_14092025_104500.zip"
    echo "  $0 --dry-run                         # Предварительный просмотр"
}

# Параметры по умолчанию
FORCE=false
DRY_RUN=false
ARCHIVE_FILE=""

# Обработка аргументов командной строки
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -*)
            error "Неизвестная опция: $1"
            show_help
            exit 1
            ;;
        *)
            if [ -z "$ARCHIVE_FILE" ]; then
                ARCHIVE_FILE="$1"
            else
                error "Слишком много аргументов"
                show_help
                exit 1
            fi
            shift
            ;;
    esac
done

# Если архив не указан, предлагаем выбрать интерактивно
if [ -z "$ARCHIVE_FILE" ]; then
    echo ""
    log "Файл архива не указан. Давайте найдем доступные резервные копии..."
    echo ""
    
    # Ищем архивы в стандартных местах
    FOUND_ARCHIVES=()
    
    # Поиск в папке Загрузки
    if [ -d "$HOME/Downloads" ]; then
        while IFS= read -r -d '' file; do
            FOUND_ARCHIVES+=("$file")
        done < <(find "$HOME/Downloads" -name "tdp_*.zip" -print0 2>/dev/null)
    fi
    
    # Поиск на Рабочем столе
    if [ -d "$HOME/Desktop" ]; then
        while IFS= read -r -d '' file; do
            FOUND_ARCHIVES+=("$file")
        done < <(find "$HOME/Desktop" -name "tdp_*.zip" -print0 2>/dev/null)
    fi
    
    # Поиск в текущей директории
    while IFS= read -r -d '' file; do
        FOUND_ARCHIVES+=("$file")
    done < <(find . -maxdepth 1 -name "tdp_*.zip" -print0 2>/dev/null)
    
    if [ ${#FOUND_ARCHIVES[@]} -eq 0 ]; then
        error "Не найдено ни одного архива TDP в стандартных местах"
        echo ""
        log "Проверьте следующие директории:"
        echo "  - $HOME/Downloads"
        echo "  - $HOME/Desktop"
        echo "  - $(pwd)"
        echo ""
        log "Или укажите полный путь к архиву:"
        echo "  $0 /path/to/your/backup.zip"
        exit 1
    fi
    
    echo "Найдены следующие резервные копии:"
    echo ""
    for i in "${!FOUND_ARCHIVES[@]}"; do
        file="${FOUND_ARCHIVES[$i]}"
        size=$(du -h "$file" | cut -f1)
        date=$(stat -f "%Sm" -t "%d.%m.%Y %H:%M" "$file" 2>/dev/null || stat -c "%y" "$file" 2>/dev/null | cut -d' ' -f1,2 | cut -d'.' -f1)
        echo "  $((i+1)). $(basename "$file") ($size, $date)"
    done
    echo "  $(( ${#FOUND_ARCHIVES[@]} + 1 )). Указать путь вручную"
    echo ""
    
    # Запрашиваем выбор
    while true; do
        read -p "Выберите номер архива (1-$(( ${#FOUND_ARCHIVES[@]} + 1 ))): " choice
        
        if [[ "$choice" =~ ^[0-9]+$ ]]; then
            if [ "$choice" -ge 1 ] && [ "$choice" -le "${#FOUND_ARCHIVES[@]}" ]; then
                ARCHIVE_FILE="${FOUND_ARCHIVES[$((choice-1))]}"
                break
            elif [ "$choice" -eq $(( ${#FOUND_ARCHIVES[@]} + 1 )) ]; then
                echo ""
                read -p "Введите полный путь к архиву: " ARCHIVE_FILE
                if [ -f "$ARCHIVE_FILE" ]; then
                    break
                else
                    error "Файл не найден: $ARCHIVE_FILE"
                    echo ""
                fi
            else
                error "Неверный номер. Выберите от 1 до $(( ${#FOUND_ARCHIVES[@]} + 1 ))"
            fi
        else
            error "Введите корректный номер"
        fi
    done
    
    echo ""
    log "Выбран архив: $ARCHIVE_FILE"
fi

# Проверяем, что мы находимся в корневой директории проекта
if [ ! -f "manage.py" ]; then
    error "Скрипт должен быть запущен из корневой директории Django проекта"
    exit 1
fi

# Проверяем существование архива
if [ ! -f "$ARCHIVE_FILE" ]; then
    error "Архив не найден: $ARCHIVE_FILE"
    echo ""
    log "Доступные резервные копии TDP в папке Загрузки:"
    ls -la "$HOME/Downloads/tdp_*.zip" 2>/dev/null || echo "  Нет резервных копий в папке Загрузки"
    echo ""
    log "Доступные резервные копии TDP на Рабочем столе:"
    ls -la "$HOME/Desktop/tdp_*.zip" 2>/dev/null || echo "  Нет резервных копий на Рабочем столе"
    echo ""
    log "Примеры использования:"
    echo "  $0 ~/Downloads/tdp_14092025_110740.zip"
    echo "  $0 ~/Desktop/tdp_14092025_110740.zip"
    echo "  $0 /path/to/your/backup.zip"
    exit 1
fi

log "Начинаем восстановление из архива: $ARCHIVE_FILE"

# Проверяем, что это ZIP архив
if ! file "$ARCHIVE_FILE" | grep -q "Zip archive"; then
    error "Файл не является ZIP архивом: $ARCHIVE_FILE"
    exit 1
fi

# Создаем временную директорию для извлечения
TEMP_DIR=$(mktemp -d)
log "Временная директория: $TEMP_DIR"

# Извлекаем архив
log "Извлекаем архив..."
unzip -q "$ARCHIVE_FILE" -d "$TEMP_DIR"

# Определяем пути к базе данных и медиа файлам из настроек Django
log "Определяем пути к данным из настроек Django..."

# Получаем путь к базе данных
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

if [ -z "$DB_PATH" ] || [ -z "$MEDIA_PATH" ]; then
    error "Не удалось определить пути к данным из настроек Django"
    error "Попробуйте установить переменную окружения DJANGO_SETTINGS_MODULE"
    rm -rf "$TEMP_DIR"
    exit 1
fi

log "База данных: $DB_PATH"
log "Медиа файлы: $MEDIA_PATH"

# Проверяем содержимое архива
if [ ! -f "$TEMP_DIR/db.sqlite3" ]; then
    error "В архиве не найдена база данных db.sqlite3"
    rm -rf "$TEMP_DIR"
    exit 1
fi

if [ ! -d "$TEMP_DIR/media" ]; then
    warning "В архиве не найдена директория media"
fi

# Показываем информацию о бэкапе если есть
if [ -f "$TEMP_DIR/backup_info.txt" ]; then
    log "Информация о резервной копии:"
    cat "$TEMP_DIR/backup_info.txt"
    echo ""
fi

# Показываем что будет восстановлено
log "Будет восстановлено:"
echo "  - База данных: $DB_PATH"
if [ -d "$TEMP_DIR/media" ]; then
    echo "  - Медиа файлы: $MEDIA_PATH ($(du -sh "$TEMP_DIR/media" | cut -f1))"
fi

# Если это dry-run, показываем и выходим
if [ "$DRY_RUN" = true ]; then
    log "Режим dry-run: изменения не будут применены"
    rm -rf "$TEMP_DIR"
    exit 0
fi

# Запрашиваем подтверждение если не принудительный режим
if [ "$FORCE" = false ]; then
    echo ""
    warning "ВНИМАНИЕ: Это действие перезапишет текущую базу данных и медиа файлы!"
    read -p "Продолжить? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log "Восстановление отменено"
        rm -rf "$TEMP_DIR"
        exit 0
    fi
fi

# Останавливаем Django сервер если он запущен
log "Проверяем запущенные Django процессы..."
if pgrep -f "manage.py runserver" > /dev/null; then
    warning "Обнаружен запущенный Django сервер. Останавливаем..."
    pkill -f "manage.py runserver" || true
    sleep 2
fi

# Создаем резервную копию текущих файлов
BACKUP_TIMESTAMP=$(date +"%d%m%Y_%H%M%S")
CURRENT_BACKUP_DIR="$HOME/Downloads/tdp_current_backup_$BACKUP_TIMESTAMP"
mkdir -p "$CURRENT_BACKUP_DIR"

log "Создаем резервную копию текущих файлов в $CURRENT_BACKUP_DIR"

if [ -f "$DB_PATH" ]; then
    cp "$DB_PATH" "$CURRENT_BACKUP_DIR/db.sqlite3"
    log "  - Текущая база данных сохранена: $DB_PATH"
fi

if [ -d "$MEDIA_PATH" ]; then
    cp -r "$MEDIA_PATH" "$CURRENT_BACKUP_DIR/media"
    log "  - Текущие медиа файлы сохранены: $MEDIA_PATH"
fi

# Восстанавливаем базу данных
log "Восстанавливаем базу данных..."
cp "$TEMP_DIR/db.sqlite3" "$DB_PATH"
success "База данных восстановлена: $DB_PATH"

# Восстанавливаем медиа файлы
if [ -d "$TEMP_DIR/media" ]; then
    log "Восстанавливаем медиа файлы..."
    rm -rf "$MEDIA_PATH"
    cp -r "$TEMP_DIR/media" "$MEDIA_PATH"
    success "Медиа файлы восстановлены: $MEDIA_PATH"
fi

# Очищаем временную директорию
rm -rf "$TEMP_DIR"

# Проверяем целостность базы данных
log "Проверяем целостность базы данных..."
if python manage.py check --deploy > /dev/null 2>&1; then
    success "База данных прошла проверку целостности"
else
    warning "База данных не прошла проверку целостности, но восстановление завершено"
fi

# Применяем миграции если нужно
log "Проверяем миграции..."
if python manage.py showmigrations --plan | grep -q "\[ \]"; then
    log "Применяем миграции..."
    python manage.py migrate --noinput
    success "Миграции применены"
else
    log "Миграции актуальны"
fi

# Собираем статические файлы
log "Собираем статические файлы..."
python manage.py collectstatic --noinput > /dev/null
success "Статические файлы собраны"

echo ""
success "Восстановление завершено успешно!"
log "Текущие файлы сохранены в: $CURRENT_BACKUP_DIR"
log "Можете запустить сервер командой: python manage.py runserver"