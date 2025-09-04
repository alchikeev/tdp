# Инструкция по деплою TDP

## Обзор

Проект настроен для деплоя на VPS с использованием Docker Compose. Caddy настроен отдельно на сервере как reverse proxy.

## Структура

- **tdp-web**: Django приложение (порт 8000)
- **Caddy**: Настроен отдельно на сервере, проксирует запросы к tdp-web:8000
- **Volumes**: Все данные сохраняются в Docker volumes

## Volumes

Все данные сохраняются в Docker volumes и не теряются при перезапуске:

- `tdp_static_data`: Статические файлы Django
- `tdp_media_data`: Медиа файлы (изображения, документы)
- `tdp_data`: База данных SQLite

## Деплой

### Автоматический деплой

```bash
./deploy.sh
```

Скрипт выполняет:
1. Получение последней версии из GitHub
2. Остановку старых контейнеров
3. Создание новых volumes с правильными правами
4. Сборку Docker образа
5. Применение миграций
6. Сборку статических файлов
7. Запуск контейнеров

### Ручной деплой

```bash
# Остановка
docker compose down

# Сборка и запуск
docker compose up -d --build

# Применение миграций
docker compose run --rm tdp-web python manage.py migrate

# Сборка статики
docker compose run --rm tdp-web python manage.py collectstatic --noinput
```

## Мониторинг

### Проверка статуса

```bash
# Статус контейнеров
docker compose ps

# Логи
docker compose logs -f tdp-web

# Health check
curl http://localhost:8000/health/
```

### Полезные команды

```bash
# Вход в контейнер
docker compose exec tdp-web bash

# Создание суперпользователя
docker compose run --rm tdp-web python manage.py createsuperuser

# Бэкап базы данных
docker compose run --rm tdp-web python manage.py dumpdata > backup.json

# Восстановление базы данных
docker compose run --rm tdp-web python manage.py loaddata backup.json
```

## Конфигурация

### Переменные окружения

Создайте файл `.env` с необходимыми переменными:

```env
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=thaidreamphuket.com,www.thaidreamphuket.com
CSRF_TRUSTED_ORIGINS=https://thaidreamphuket.com,https://www.thaidreamphuket.com
DATABASE_URL=sqlite:///data/db.sqlite3
STATIC_ROOT=/app/staticfiles
MEDIA_ROOT=/app/media
```

### Caddy

Caddy настроен отдельно на сервере и автоматически получает SSL сертификаты от Let's Encrypt. Конфигурация находится в `/srv/reverse-proxy/caddy/sites/tdp.caddy`.

## Безопасность

- Все HTTP запросы перенаправляются на HTTPS
- Настроены заголовки безопасности (HSTS, CSP, XSS защита)
- Django работает с правильными заголовками прокси
- Контейнеры запускаются от непривилегированного пользователя

## Troubleshooting

### Проблемы с правами доступа

```bash
# Исправление прав для volumes
docker run --rm -v tdp_static_data:/data alpine chown -R 1000:1000 /data
docker run --rm -v tdp_media_data:/data alpine chown -R 1000:1000 /data
docker run --rm -v tdp_data:/data alpine chown -R 1000:1000 /data
```

### Проблемы с SSL

```bash
# Перезапуск Caddy на сервере
docker restart caddy
```

### Проблемы с базой данных

```bash
# Пересоздание базы данных
docker volume rm tdp_data
docker compose run --rm tdp-web python manage.py migrate
```
