from django.urls import path
from . import views # Assuming your dashboard views are here

urlpatterns = [
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
]