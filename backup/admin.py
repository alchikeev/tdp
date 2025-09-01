# backup/admin.py
from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path

from .models import Backup
from . import views


@admin.register(Backup)
class BackupAdmin(admin.ModelAdmin):
    # наш собственный шаблон списка — без запросов к БД
    change_list_template = "admin/backup_change_list.html"

    def get_urls(self):
        """
        Добавляем две ручки прямо под /admin/backup/backup/:
        - /download/  -> выгрузка архива
        - /restore/   -> загрузка архива
        Имена маршрутов соответствуют паттерну admin:<app>_<model>_<name>
        """
        urls = super().get_urls()
        info = (self.model._meta.app_label, self.model._meta.model_name)
        my = [
            path(
                "download/",
                self.admin_site.admin_view(views.backup_download),
                name=f"{info[0]}_{info[1]}_download",
            ),
            path(
                "restore/",
                self.admin_site.admin_view(views.backup_restore),
                name=f"{info[0]}_{info[1]}_restore",
            ),
        ]
        return my + urls

    def changelist_view(self, request, extra_context=None):
        ctx = {"title": "Резервные копии"}
        if extra_context:
            ctx.update(extra_context)
        # ВАЖНО: не вызываем super().changelist_view(), чтобы не лезть в БД
        return TemplateResponse(request, self.change_list_template, ctx)
