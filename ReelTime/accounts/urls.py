from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_user, name='register'), # User Registration
    path('register-admin/', views.register_admin, name='register_admin'), # Admin Registration
    path('login/', views.login_user, name='login'), # User Login
    path('logout/', views.logout_user, name='logout'), # Logout URL
    path('change-password/', views.change_password, name='change_password'), # Change Password
    path('profile/', views.profile_view, name='profile'), # Profile URL
    path('edit-profile/', views.edit_profile, name='edit_profile'), # Edit Profile URL
]
