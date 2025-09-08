# TDP - Thai Dream Phuket

Веб-сайт туристического агентства с Django и Docker.

## Быстрый старт

### 1. Подготовка окружения

```bash
# Клонируйте репозиторий
git clone https://github.com/alchikeev/tdp.git
cd tdp

# Скопируйте файл окружения
cp env.example .env

# Отредактируйте .env файл под ваши нужды
nano .env
```

### 2. Проверка и деплой

```bash
# Проверить миграции и настройки
make check

# Применить миграции
make migrate

# Собрать статические файлы
make static

# Запустить все сервисы
make up

# Или полный деплой одной командой
make deploy
```

### 3. Управление сервисами

```bash
# Показать логи
make logs

# Остановить сервисы
make down

# Перезагрузить Caddy
make reload-caddy

# Очистить Docker ресурсы
make clean
```

## Архитектура

- **web** - Django приложение (порт 8000, только внутри Docker сети)
- **caddy** - Веб-сервер для раздачи статики и проксирования (порты 80, 443)

## Структура проекта

```
tdp/
├── docker/
│   └── entrypoint.sh      # Скрипт запуска Django
├── config/
│   └── settings/          # Настройки Django
├── static/                # Исходные статические файлы
├── templates/             # Шаблоны Django
├── media/                 # Медиа файлы
├── compose.yml            # Docker Compose конфигурация
├── Dockerfile             # Docker образ для Django
├── Makefile              # Команды для управления
└── README.md             # Этот файл
```

## Переменные окружения

Основные переменные в `.env`:

```bash
# Django настройки
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# База данных
DATABASE_URL=sqlite:////app/data/db.sqlite3

# Статика и медиа (пути внутри контейнера)
DJANGO_STATIC_ROOT=/srv/static_tdp
DJANGO_MEDIA_ROOT=/srv/media_tdp

# Логирование
LOG_LEVEL=INFO
```

## Volumes

- `static_tdp` - собранные статические файлы Django
- `media_tdp` - медиа файлы (загруженные пользователями)
- `caddy_data` - данные Caddy
- `caddy_config` - конфигурация Caddy

## Troubleshooting

### Проблемы с правами доступа

Если возникают ошибки PermissionError:

```bash
# Пересобрать образ
make build

# Запустить заново
make up
```

### Проблемы с миграциями

```bash
# Проверить статус миграций
make check

# Применить миграции
make migrate
```

### Проблемы со статикой

```bash
# Пересобрать статику
make static

# Перезапустить Caddy
make reload-caddy
```

## Разработка

Для разработки используйте:

```bash
# Запуск в режиме разработки
make dev-up

# Логи разработки
make dev-logs
```

## Производство

1. Настройте домен в `.env`
2. Настройте SSL в `tdp.caddy`
3. Запустите: `make deploy`
4. Проверьте: `make logs`
