import os
from celery import Celery

# Устанавливаем переменную окружения для Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.prod')

app = Celery('tdp')

# Используем строку для автоматического обнаружения задач
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматическое обнаружение задач из всех приложений Django
app.autodiscover_tasks()

# Настройки для продакшена
app.conf.update(
    broker_url='redis://79.133.181.1:6379/0',
    result_backend='redis://79.133.181.1:6379/0',
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Bishkek',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 минут
    task_soft_time_limit=25 * 60,  # 25 минут
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
