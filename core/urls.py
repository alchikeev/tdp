
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('lead/create/', views.lead_create, name='lead_create'),
]
