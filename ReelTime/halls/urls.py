from . import views
from django.urls import path

urlpatterns = [
    path("", views.hall_list, name="hall_list"),
    path("add/", views.hall_form_view, name="hall_add"),
    path("<int:pk>/edit/", views.hall_form_view, name="hall_edit"),
    path("<int:pk>/delete/", views.hall_delete, name="hall_delete"),
]