# config/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from core.views import home, health_ok

urlpatterns = [
    # backup admin UI is integrated via admin changelist for the Backup proxy model
    path("", home, name="home"),
    path("health/", health_ok, name="health"),
    path("api/", include(("core.urls", "core"), namespace="core")),
    path("tours/", include(("tours.urls", "tours"), namespace="tours")),
    path("services/", include(("services.urls", "services"), namespace="services")),
    path("prices/", include(("prices.urls", "prices"), namespace="prices")),
    path("reviews/", include(("reviews.urls", "reviews"), namespace="reviews")),
    path("admin/", admin.site.urls),
    path("news/", include(("news.urls", "news"), namespace="news")),
    path("blog/", include(("blog.urls", "blog"), namespace="blog")),
    path("typography/", TemplateView.as_view(template_name="typography_demo.html"), name="typography_demo"),
]

if settings.DEBUG:
    # Раздача медиа-файлов (картинки и т.д.)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Раздача статических файлов (CSS, JS) из папки static
    urlpatterns += static(settings.STATIC_URL, document_root=str(settings.STATICFILES_DIRS[0]))
