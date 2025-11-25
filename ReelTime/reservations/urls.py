from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_reservations_view, name='reservations'),
    path('edit/<int:reservation_id>/', views.edit_reservation, name='edit_reservation'),
    path('cancel/<int:reservation_id>/', views.cancel_reservation, name='cancel_reservation'),
    path('delete/<int:reservation_id>/', views.delete_reservation, name='delete_reservation'),
]
