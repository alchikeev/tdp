from django.db import models
from core.models import SiteSettings


# Proxy model based on SiteSettings so admin can show a section without new table
class Backup(SiteSettings):
    class Meta:
        proxy = True
        verbose_name = 'Резервное копирование'
        verbose_name_plural = 'Резервное копирование'

    def __str__(self):
        return 'Резервное копирование'
