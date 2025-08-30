Thai Dream Phuket — проект TDP

Коротко: Django + simple frontend. Документация по локальной разработке и прод-деплою ниже.

## Прод-деплой Docker + Caddy

Требования:
- Docker
- Docker Compose

Шаги:
1. Скопируйте пример окружения и отредактируйте секреты и домены:

```bash
cp .env.example .env
# отредактируйте .env — SECRET_KEY, ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS и т.д.
```

2. Соберите и запустите сервисы:

```bash
docker compose build --no-cache
docker compose up -d
```

3. Выполните миграции и соберите статические файлы:

```bash
docker compose exec tdp python manage.py migrate
docker compose exec tdp python manage.py collectstatic --noinput
```

4. Создайте админа (опционально):

```bash
docker compose exec -T tdp python manage.py createsuperuser
```

DNS (пример для GoDaddy):
- A запись для `@` → IP сервера
- CNAME для `www` → `thaidreamphuket.com`

Логи для отладки:

```bash
docker compose logs -f tdp
docker compose logs -f caddy
```

Проверки:
- Прямой доступ к бэкенду: http://SERVER_IP:8000
- Прод: https://thaidreamphuket.com

Частые проблемы:
- CSRF / ALLOWED_HOSTS: заполните `.env` корректно (ALLOWED_HOSTS и CSRF_TRUSTED_ORIGINS должны быть указаны).
- Прокси-заголовки: Caddy добавляет `X-Forwarded-Proto` — настройки `SECURE_PROXY_SSL_HEADER` в `.env` и `USE_X_FORWARDED_HOST=True` в `config/settings.py` уже предусмотрены.
- sw.js 404: добавьте `static/sw.js` и выполните collectstatic, если используете PWA.

