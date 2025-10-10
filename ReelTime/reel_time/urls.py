from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='index'),  # Root URL
    path('dashboards/', include('dashboards.urls')),  # Include dashboards app URLs
    path('accounts/', include('accounts.urls')),  # Include accounts app URLs
]