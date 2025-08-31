# backup/urls.py
from django.urls import path
from . import views

app_name = 'backup'

urlpatterns = [
    # этот name намеренно совпадает с тем, что использовалось в админке:
    # reverse('admin:backup_backup_changelist')
    path('', views.backup_index, name='backup_backup_changelist'),
    path('download/', views.backup_download, name='download'),
    path('restore/', views.backup_restore, name='restore'),
]
