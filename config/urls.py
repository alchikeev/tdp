# config/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", TemplateView.as_view(template_name="index.html"), name="home"),
    path("api/", include(("core.urls", "core"), namespace="core")),
    path("tours/", include(("tours.urls", "tours"), namespace="tours")),
    path("services/", include(("services.urls", "services"), namespace="services")),
    path("reviews/", include(("reviews.urls", "reviews"), namespace="reviews")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
