from django.db import models

class Backup(models.Model):
    """Прокси-модель для появления пункта в админке (таблица в БД не создаётся)."""
    class Meta:
        managed = False
        app_label = "backup"
        verbose_name = "Резервное копирование"
        verbose_name_plural = "Резервные копии"

    def __str__(self):
        return "Резервное копирование"
