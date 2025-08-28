from django.urls import path
from .views import ReviewListView, ReviewCreateView

app_name = 'reviews'

urlpatterns = [
    path('', ReviewListView.as_view(), name='list'),
    path('add/', ReviewCreateView.as_view(), name='add'),
]
