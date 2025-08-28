from django.db import models


class PricePDF(models.Model):
    """Хранит актуальный прайс в формате PDF, загружается через админку."""
    name = models.CharField(max_length=200, blank=True, help_text="Название файла/прайса (опционально)")
    file = models.FileField(upload_to='prices/', help_text='PDF файл с актуальными ценами')
    is_active = models.BooleanField(default=True, help_text='Отметьте, чтобы этот файл был текущим для скачивания')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_active', '-uploaded_at']

    def __str__(self):
        return self.name or (self.file.name.split('/')[-1] if self.file else 'Прайс PDF')
