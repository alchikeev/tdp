# core/urls.py
from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),  # Главная страница
    path("lead/create/", views.lead_create, name="lead_create"),
    path("api/categories/<int:category_id>/subcategories/", views.get_subcategories, name="get_subcategories"),                                                                                                         
    path("api/categories/<int:category_id>/tours/", views.get_tours_by_category, name="get_tours_by_category"),                                                                                                         
    path("api/tours/all/", views.get_all_tours, name="get_all_tours"),
]
