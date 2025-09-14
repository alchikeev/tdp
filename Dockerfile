FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . /app

# Аргумент окружения: dev|prod
ARG DJANGO_ENV=dev
ENV DJANGO_ENV=${DJANGO_ENV}

# Создаем папки для данных
RUN mkdir -p /data /app/media /app/staticfiles

# Создаем .env файлы для разных окружений
RUN echo "DJANGO_ENV=dev" > .env.dev && \
    echo "DJANGO_SECRET_KEY=dev-secret-key" >> .env.dev && \
    echo "DJANGO_DEBUG=True" >> .env.dev && \
    echo "DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1" >> .env.dev

# Сбор статики (OK, если в dev её ещё нет)
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

# Запуск приложения
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
