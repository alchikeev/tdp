from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Основные URL-ы приложений
    path('', include('core.urls')),
    path('tours/', include('tours.urls')),
    path('services/', include('services.urls')),
    path('reviews/', include('reviews.urls')),
    path('news/', include('news.urls')),
    path('blog/', include('blog.urls')),
    path('prices/', include('prices.urls')),
]
