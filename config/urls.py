from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render

def backup_page(request):
    """Страница управления резервными копиями"""
    return render(request, 'admin/backup/backup_page.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/backup/', backup_page, name='backup_page'),
    path('admin/backup/restore/', include('backup.urls')),
    
    # Основные URL-ы приложений
    path('', include('core.urls')),
    path('tours/', include('tours.urls')),
    path('services/', include('services.urls')),
    path('reviews/', include('reviews.urls')),
    path('news/', include('news.urls')),
    path('blog/', include('blog.urls')),
    path('prices/', include('prices.urls')),
]
