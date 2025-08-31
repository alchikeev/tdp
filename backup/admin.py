from django.contrib import admin
from .models import Backup

@admin.register(Backup)
class BackupAdmin(admin.ModelAdmin):
    change_list_template = "admin/backup/backup/change_list.html"

    # никаких CRUD-операций не нужно
    def has_add_permission(self, request): return False
    def has_view_permission(self, request, obj=None): return True
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False
