from django.contrib import admin

from .models import Department, Faculty, StaffProfile, StudentProfile


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "campus")


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "faculty")
    list_filter = ("faculty",)


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("reg_number", "user", "department", "year_of_study", "phone")
    list_filter = ("department", "year_of_study")
    search_fields = ("reg_number", "user__first_name", "user__last_name")


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ("staff_number", "user", "position", "office")
