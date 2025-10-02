from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),  # Root URL
    path('login/', auth_views.LoginView.as_view(template_name='reel_time/login.html'), name='login'), # Login URL
]