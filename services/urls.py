from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.service_list, name='list'),
    path('category/<slug:slug>/', views.service_list_by_category, name='by_category'),
    path('tag/<slug:slug>/', views.service_list_by_tag, name='by_tag'),
    path('<slug:slug>/', views.service_detail, name='detail'),
]
