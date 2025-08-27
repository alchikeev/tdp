from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Главная рендерит templates/index.html
    path('', TemplateView.as_view(template_name='index.html'), name='home'),

    # Каталог туров
    path('tours/', include(('tours.urls', 'tours'), namespace='tours')),

    path('services/', include(('services.urls', 'services'), namespace='services')),

    # API/формы ядра (namespace=core) — ВАЖНО!
    path('api/', include(('core.urls', 'core'), namespace='core')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
