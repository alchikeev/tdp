FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ✅ сначала зависимости — так pip переустанавливается только при изменении requirements.txt
COPY app/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# затем код проекта
COPY app/ /app/

CMD ["gunicorn","config.wsgi:application","--bind","0.0.0.0:8000","--workers","3","--timeout","90","--access-logfile","-","--error-logfile","-"]
