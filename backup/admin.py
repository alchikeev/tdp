from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
import zipfile
import tempfile
import shutil
from datetime import datetime

def backup_page(request):
    """Страница управления резервными копиями"""
    return render(request, 'admin/backup/backup_page.html')

def backup_create(request):
    """Создание резервной копии"""
    if request.method == 'POST':
        try:
            # Создаем временный файл для архива
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f'TDP_backup_{timestamp}.zip'
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
                with zipfile.ZipFile(temp_file.name, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    # Добавляем базу данных
                    db_path = settings.DATABASES['default']['NAME']
                    if os.path.exists(db_path):
                        zip_file.write(db_path, 'db.sqlite3')
                    
                    # Добавляем медиа файлы
                    media_path = settings.MEDIA_ROOT
                    if os.path.exists(media_path):
                        for root, dirs, files in os.walk(media_path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, media_path)
                                zip_file.write(file_path, f'media/{arcname}')
                    
                    # Добавляем статические файлы
                    static_path = settings.STATIC_ROOT
                    if os.path.exists(static_path):
                        for root, dirs, files in os.walk(static_path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, static_path)
                                zip_file.write(file_path, f'static/{arcname}')
                
                # Перемещаем файл в медиа папку
                backup_path = os.path.join(settings.MEDIA_ROOT, backup_filename)
                shutil.move(temp_file.name, backup_path)
                
                messages.success(request, f'Резервная копия создана: {backup_filename}')
                return HttpResponseRedirect(request.path)
                
        except Exception as e:
            messages.error(request, f'Ошибка при создании резервной копии: {str(e)}')
            return HttpResponseRedirect(request.path)
    
    return render(request, 'admin/backup/backup_page.html')

def backup_restore(request):
    """Восстановление из резервной копии"""
    if request.method == 'POST':
        if 'backup_file' not in request.FILES:
            messages.error(request, 'Файл не выбран')
            return HttpResponseRedirect(request.path)
        
        uploaded_file = request.FILES['backup_file']
        
        try:
            # Сохраняем загруженный файл
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            file_name = fs.save(uploaded_file.name, uploaded_file)
            uploaded_file_path = fs.path(file_name)
            
            # Создаем временную папку для распаковки
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(uploaded_file_path, 'r') as zip_file:
                    zip_file.extractall(temp_dir)
                
                # Восстанавливаем базу данных
                db_backup_path = os.path.join(temp_dir, 'db.sqlite3')
                if os.path.exists(db_backup_path):
                    db_path = settings.DATABASES['default']['NAME']
                    shutil.copy2(db_backup_path, db_path)
                
                # Восстанавливаем медиа файлы
                media_backup_path = os.path.join(temp_dir, 'media')
                if os.path.exists(media_backup_path):
                    if os.path.exists(settings.MEDIA_ROOT):
                        shutil.rmtree(settings.MEDIA_ROOT)
                    shutil.copytree(media_backup_path, settings.MEDIA_ROOT)
                
                # Восстанавливаем статические файлы
                static_backup_path = os.path.join(temp_dir, 'static')
                if os.path.exists(static_backup_path):
                    if os.path.exists(settings.STATIC_ROOT):
                        shutil.rmtree(settings.STATIC_ROOT)
                    shutil.copytree(static_backup_path, settings.STATIC_ROOT)
            
            # Удаляем загруженный файл
            os.remove(uploaded_file_path)
            
            messages.success(request, 'Восстановление завершено успешно!')
            return HttpResponseRedirect(request.path)
            
        except Exception as e:
            messages.error(request, f'Ошибка при восстановлении: {str(e)}')
            return HttpResponseRedirect(request.path)
    
    return render(request, 'admin/backup/backup_page.html')

def get_admin_urls():
    """Добавляет URL для страницы резервных копий в админку"""
    return [
        path('backup/', backup_page, name='backup_page'),
        path('backup/create/', backup_create, name='backup_create'),
        path('backup/restore/', backup_restore, name='backup_restore'),
    ]

# Регистрируем URL в админке
admin.site.get_urls = lambda: get_admin_urls() + admin.site.get_urls()
