from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='index'),  # Root URL
    path('login/', views.login_user, name='login'), # Login URL
    path('register/', views.register_user, name='register'),  # Registration URL
    path('dashboard/', views.dashboard, name='dashboard'),  # Dashboard URL
    path('logout/', views.logout_user, name='logout'),  # Logout URL
]