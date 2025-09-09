from django.urls import path
from . import views

urlpatterns = [
    path('', views.backup_page, name='backup_page'),
    path('create/', views.backup_create, name='backup_create'),
    path('restore/', views.backup_restore, name='backup_restore'),
]
