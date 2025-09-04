# Исправление проблем с базой данных

## Проблемы
1. `attempt to write a readonly database` - неправильные права доступа к БД
2. `no such table: tours_tour` - не применены миграции

## Быстрое решение

### Автоматическое исправление
```bash
# Запустите скрипт исправления
./fix-database.sh
```

### Применение миграций (если есть непримененные)
```bash
# Примените непримененные миграции
./apply-migrations.sh
```

### Ручное исправление

#### 1. Остановите контейнер
```bash
docker compose down
```

#### 2. Удалите старую базу данных
```bash
docker volume rm tdp_data
```

#### 3. Создайте новую базу данных
```bash
docker volume create tdp_data
```

#### 4. Запустите контейнер
```bash
docker compose up -d
```

#### 5. Примените миграции
```bash
docker compose exec -e DJANGO_SETTINGS_MODULE=config.settings.prod web python manage.py migrate --run-syncdb
```

#### 6. Создайте суперпользователя
```bash
docker compose exec -e DJANGO_SETTINGS_MODULE=config.settings.prod web python manage.py createsuperuser
```

#### 7. Соберите статику
```bash
docker compose exec -e DJANGO_SETTINGS_MODULE=config.settings.prod web python manage.py collectstatic --noinput
```

## Проверка
После исправления проверьте:
- Статус: `docker compose ps`
- Логи: `docker compose logs -f web`
- База данных: `docker compose exec web ls -la /app/data/`
- Настройки Django: `./check-settings.sh`
- Сайт: https://thaidreamphuket.com
- Админка: https://thaidreamphuket.com/admin

## Полезные команды

### Проверка настроек Django
```bash
# Используйте docker compose exec (загружает .env автоматически)
docker compose exec web python manage.py shell -c "from django.conf import settings; print(settings.DATABASES['default']['NAME'])"

# Или используйте скрипт
./django-shell.sh "from django.conf import settings; print(settings.DATABASES['default']['NAME'])"
```

### Проверка всех настроек
```bash
./check-settings.sh
```
