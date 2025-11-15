from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='index'), 
    path('dashboards/', include('dashboards.urls')),
    path('accounts/', include('accounts.urls')),
    path('movies/', include('movies.urls')),
    path('reservations/', include('reservations.urls')),
    path('halls/', include('halls.urls')),
    path('dashboards/user_dashboard/', views.user_dashboard_view, name='user_dashboard'),
]
