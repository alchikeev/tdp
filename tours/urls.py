# tours/urls.py
from django.urls import path
from . import views

app_name = "tours"

urlpatterns = [
    path("", views.tour_list, name="list"),
    path("category/<slug:slug>/", views.tour_list_by_category, name="by_category"),
    path("tag/<slug:slug>/", views.tour_list_by_tag, name="by_tag"),
    path("<slug:slug>/", views.tour_detail, name="detail"),
]

