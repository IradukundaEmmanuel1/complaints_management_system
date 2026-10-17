"""App-level URLs for the accounts app (all staff only)."""
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    # Faculties
    path("faculties/", views.faculty_list, name="faculty_list"),
    path("faculties/add/", views.faculty_create, name="faculty_create"),
    path("faculties/<int:pk>/", views.faculty_detail, name="faculty_detail"),
    path("faculties/<int:pk>/edit/", views.faculty_update, name="faculty_update"),
    path("faculties/<int:pk>/delete/", views.faculty_delete, name="faculty_delete"),
    # Departments
    path("departments/", views.department_list, name="department_list"),
    path("departments/add/", views.department_create, name="department_create"),
    path("departments/<int:pk>/", views.department_detail, name="department_detail"),
    path("departments/<int:pk>/edit/", views.department_update, name="department_update"),
    path("departments/<int:pk>/delete/", views.department_delete, name="department_delete"),
    # Students
    path("students/", views.student_list, name="student_list"),
    path("students/<int:pk>/", views.student_detail, name="student_detail"),
    path("students/<int:pk>/edit/", views.student_update, name="student_update"),
    path("students/<int:pk>/delete/", views.student_delete, name="student_delete"),
    # Staff
    path("staff/", views.staff_list, name="staff_list"),
    path("staff/<int:pk>/", views.staff_detail, name="staff_detail"),
    path("staff/<int:pk>/edit/", views.staff_update, name="staff_update"),
    path("staff/<int:pk>/delete/", views.staff_delete, name="staff_delete"),
]
