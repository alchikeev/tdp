# backup/models.py
from django.db import models
from core.models import SiteSettings


class Backup(SiteSettings):
    """
    Proxy-модель на существующую таблицу core_sitesettings.
    Нужна только для того, чтобы получить пункт меню в админке
    и базовый URL /admin/backup/backup/.
    """
    class Meta:
        proxy = True
        app_label = "backup"
        verbose_name = "Резервная копия"
        verbose_name_plural = "Резервные копии"