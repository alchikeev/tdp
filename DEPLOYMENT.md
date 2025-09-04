# Деплой TDP на VPS

## Подготовка

1. Убедитесь, что на VPS запущен общий контейнер Caddy и создана сеть `web`
2. Скопируйте файлы проекта на VPS
3. Создайте файл `.env` на основе `.env.example`

## Быстрый деплой

```bash
# Запустить деплой (автоматически получает последнюю версию из GitHub)
./deploy.sh
```

Скрипт автоматически:
- Получает последнюю версию из GitHub
- Останавливает старый контейнер
- Собирает новый Docker образ
- Применяет миграции и собирает статику
- Запускает новый контейнер
- Очищает старые образы

## Ручной деплой

```bash
# Собрать статику
docker-compose run --rm tdp python manage.py collectstatic --noinput

# Применить миграции
docker-compose run --rm tdp python manage.py migrate

# Запустить контейнер
docker-compose up -d
```

## Проверка

- Статус: `docker-compose ps`
- Логи: `docker-compose logs -f web`
- Health check: `curl http://localhost:8000/health/`

## Обновление

```bash
# Остановить контейнер
docker-compose down

# Обновить код
git pull

# Пересобрать и запустить
docker-compose up -d --build
```
