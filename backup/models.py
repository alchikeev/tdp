from django.db import models
from django.contrib.auth.models import User
import uuid

class RestoreTask(models.Model):
    """Модель для отслеживания задач восстановления"""
    
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('processing', 'Обрабатывается'),
        ('completed', 'Завершено'),
        ('failed', 'Ошибка'),
        ('cancelled', 'Отменено'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    filename = models.CharField(max_length=255, verbose_name='Имя файла')
    file_size = models.BigIntegerField(verbose_name='Размер файла (байт)')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    progress = models.IntegerField(default=0, verbose_name='Прогресс (%)')
    message = models.TextField(blank=True, verbose_name='Сообщение')
    error_details = models.TextField(blank=True, verbose_name='Детали ошибки')
    
    # Статистика восстановления
    imported_categories = models.IntegerField(default=0, verbose_name='Импортировано категорий')
    imported_tags = models.IntegerField(default=0, verbose_name='Импортировано тегов')
    imported_tours = models.IntegerField(default=0, verbose_name='Импортировано туров')
    imported_services = models.IntegerField(default=0, verbose_name='Импортировано услуг')
    imported_reviews = models.IntegerField(default=0, verbose_name='Импортировано отзывов')
    imported_news = models.IntegerField(default=0, verbose_name='Импортировано новостей')
    imported_blog = models.IntegerField(default=0, verbose_name='Импортировано статей')
    imported_prices = models.IntegerField(default=0, verbose_name='Импортировано прайсов')
    imported_files = models.IntegerField(default=0, verbose_name='Импортировано файлов')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='Начато')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Завершено')
    
    class Meta:
        verbose_name = 'Задача восстановления'
        verbose_name_plural = 'Задачи восстановления'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.filename} - {self.get_status_display()}'
    
    @property
    def duration(self):
        """Длительность выполнения задачи"""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None
