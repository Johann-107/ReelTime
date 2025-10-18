from django.urls import path
from . import views

urlpatterns = [
    path('add_movie/', views.add_movie, name='add_movie'),
    path('movie_list/', views.movie_list_view, name='movie_list'),
]
