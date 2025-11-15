from django.urls import path
from . import views

urlpatterns = [
    path('reservations/', views.user_reservations_view, name='reservations'),
]
