from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='index'),  # Root URL
    path('login/', views.login_user, name='login'), # Login URL
    path('register/', views.register_user, name='register'),  # Registration URL
    path('dashboard/', views.user_dashboard, name='user_dashboard'),  # Dashboard URL
    path('logout/', views.logout_user, name='logout'),  # Logout URL
    path('profile/', views.profile_view, name='profile'),  # Profile URL
    path('profile/edit/', views.edit_profile, name='edit_profile'), # Edit Profile URL
    path('register-admin/', views.register_admin, name='register_admin'), # Admin Registration
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'), # Admin Dashboard
    path('change-password/', views.change_password, name='change_password'), # Change Password
]