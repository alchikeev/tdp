# config/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from core.views import home

urlpatterns = [
    path("admin/", admin.site.urls),
    # backup admin UI is integrated via admin changelist for the Backup proxy model
    path("", home, name="home"),
    path("api/", include(("core.urls", "core"), namespace="core")),
    path("tours/", include(("tours.urls", "tours"), namespace="tours")),
    path("services/", include(("services.urls", "services"), namespace="services")),
    path("prices/", include(("prices.urls", "prices"), namespace="prices")),
    path("reviews/", include(("reviews.urls", "reviews"), namespace="reviews")),
]

if settings.DEBUG:
    # Раздача медиа-файлов (картинки и т.д.)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Раздача статических файлов (CSS, JS) из папки static
    urlpatterns += static(settings.STATIC_URL, document_root=str(settings.STATICFILES_DIRS[0]))
