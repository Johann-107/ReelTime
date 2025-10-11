from django.urls import path
from . import views # Assuming your dashboard views are here

urlpatterns = [
    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]