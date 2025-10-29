from django.urls import path
from . import views

urlpatterns = [
    path('add_movie/', views.add_movie, name='add_movie'), 
    path('movie_list/', views.movie_list_view, name='movie_list'),
    path('<int:pk>/', views.movie_detail_view, name='movie_detail'),
    path('<int:pk>/edit/', views.edit_movie_view, name='edit_movie'),
    path('<int:pk>/delete/', views.delete_movie_view, name='delete_movie'),
    path('reserve/<int:movie_id>/', views.reserve_movie_view, name='reserve_movie'),
    path('confirm/<int:detail_id>/', views.confirm_reservation_view, name='confirm_reservation'),
    path('reservations/', views.user_reservations_view, name='reservations'),
]
