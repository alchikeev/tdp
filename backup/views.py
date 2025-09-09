# backup/views.py
from django.shortcuts import render
from django.conf import settings

def backup_page(request):
    """Страница управления резервными копиями"""
    context = {
        'db_path': settings.DATABASES['default']['NAME'],
        'media_path': settings.MEDIA_ROOT,
        'static_path': settings.STATIC_ROOT,
    }
    return render(request, 'admin/backup/backup_page.html', context)
