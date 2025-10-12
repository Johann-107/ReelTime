from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='index'), 
    path('movies/', views.movie_list_view, name='movies'),
    path('dashboards/', include('dashboards.urls')),
    path('accounts/', include('accounts.urls')),
    path('dashboards/user-dashboard/', views.user_dashboard_view, name='user_dashboard'),
]