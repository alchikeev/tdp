# Исправление проблемы с базой данных

## Проблема
Ошибка `attempt to write a readonly database` возникает из-за неправильных прав доступа к базе данных SQLite.

## Решение

### 1. Остановите контейнер
```bash
docker compose down
```

### 2. Создайте необходимые volumes
```bash
docker volume create tdp_static_data
docker volume create tdp_media_data
docker volume create tdp_data
```

### 3. Запустите обновленный скрипт деплоя
```bash
./deploy.sh
```

## Альтернативное решение (если проблема остается)

### 1. Создайте директорию для данных
```bash
mkdir -p /srv/tdp/data
chmod 777 /srv/tdp/data
```

### 2. Обновите compose.yml для использования bind mount
```yaml
volumes:
  - tdp_static_data:/app/staticfiles
  - tdp_media_data:/app/media
  - ./data:/app/data
```

### 3. Запустите деплой
```bash
./deploy.sh
```

## Проверка
После исправления проверьте:
- Статус: `docker compose ps`
- Логи: `docker compose logs -f web`
- База данных: `docker compose exec web ls -la /app/data/`
