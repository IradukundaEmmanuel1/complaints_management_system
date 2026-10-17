"""App-level URLs for the complaints app."""
from django.urls import path

from . import views

app_name = "complaints"

urlpatterns = [
    # Complaints
    path("", views.complaint_list, name="complaint_list"),
    path("new/", views.complaint_create, name="complaint_create"),
    path("status/<str:status>/", views.complaints_by_status, name="complaints_by_status"),
    path("<int:pk>/", views.complaint_detail, name="complaint_detail"),
    path("<int:pk>/edit/", views.complaint_update, name="complaint_update"),
    path("<int:pk>/delete/", views.complaint_delete, name="complaint_delete"),
    # Categories (staff only)
    path("categories/", views.category_list, name="category_list"),
    path("categories/add/", views.category_create, name="category_create"),
    path("categories/<int:pk>/", views.category_detail, name="category_detail"),
    path("categories/<int:pk>/edit/", views.category_update, name="category_update"),
    path("categories/<int:pk>/delete/", views.category_delete, name="category_delete"),
]
