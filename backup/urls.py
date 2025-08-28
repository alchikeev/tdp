from django.urls import path
from . import views

app_name = 'backup'

urlpatterns = [
    path('', views.backup_index, name='index'),
    path('download/', views.backup_download, name='download'),
    path('restore/', views.backup_restore, name='restore'),
]
