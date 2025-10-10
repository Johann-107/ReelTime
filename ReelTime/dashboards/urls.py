from django.urls import path
from . import views

urlpatterns = [
    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),  # Dashboard URL
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'), # Admin Dashboard
]