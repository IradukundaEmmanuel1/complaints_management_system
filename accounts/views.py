from django.contrib import messages
from django.contrib.auth import login
from django.db.models import Count, ProtectedError
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (DepartmentForm, FacultyForm, StaffProfileForm, StudentProfileForm,
                    StudentRegistrationForm)
from .models import Department, Faculty, StaffProfile, StudentProfile
from .permissions import staff_required


# ---------------- Student sign-up (public) ----------------

def register(request):
    form = StudentRegistrationForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)   # log the new student in straight away
        messages.success(request, f"Welcome {user.first_name}! Your student account was created.")
        return redirect("dashboard")
    return render(request, "registration/register.html", {"form": form})


# ---------------- Faculties ----------------

@staff_required
def faculty_list(request):
    faculties = Faculty.objects.annotate(num_departments=Count("departments"))
    return render(request, "accounts/faculty_list.html", {"faculties": faculties})


@staff_required
def faculty_detail(request, pk):
    faculty = get_object_or_404(Faculty, pk=pk)
    departments = faculty.departments.annotate(num_students=Count("students"))
    return render(request, "accounts/faculty_detail.html", {"faculty": faculty, "departments": departments})


@staff_required
def faculty_create(request):
    form = FacultyForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Faculty added successfully.")
        return redirect("accounts:faculty_list")
    return render(request, "form.html", {"form": form, "title": "Add Faculty", "cancel_url": "accounts:faculty_list"})


@staff_required
def faculty_update(request, pk):
    faculty = get_object_or_404(Faculty, pk=pk)
    form = FacultyForm(request.POST or None, instance=faculty)
    if form.is_valid():
        form.save()
        messages.success(request, "Faculty updated successfully.")
        return redirect("accounts:faculty_list")
    return render(request, "form.html", {"form": form, "title": "Edit Faculty", "cancel_url": "accounts:faculty_list"})


@staff_required
def faculty_delete(request, pk):
    faculty = get_object_or_404(Faculty, pk=pk)
    if request.method == "POST":   # user clicked "Yes, delete" on the confirmation page
        try:
            faculty.delete()
            messages.success(request, "Faculty deleted successfully.")
        except ProtectedError:
            messages.error(request, "Cannot delete: this faculty still has departments.")
        return redirect("accounts:faculty_list")
    return render(request, "confirm_delete.html", {"object": faculty, "cancel_url": "accounts:faculty_list"})


# ---------------- Departments ----------------

@staff_required
def department_list(request):
    departments = Department.objects.select_related("faculty").annotate(num_students=Count("students"))
    return render(request, "accounts/department_list.html", {"departments": departments})


@staff_required
def department_detail(request, pk):
    department = get_object_or_404(Department, pk=pk)
    students = department.students.select_related("user")
    return render(request, "accounts/department_detail.html", {"department": department, "students": students})


@staff_required
def department_create(request):
    form = DepartmentForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Department added successfully.")
        return redirect("accounts:department_list")
    return render(request, "form.html", {"form": form, "title": "Add Department", "cancel_url": "accounts:department_list"})


@staff_required
def department_update(request, pk):
    department = get_object_or_404(Department, pk=pk)
    form = DepartmentForm(request.POST or None, instance=department)
    if form.is_valid():
        form.save()
        messages.success(request, "Department updated successfully.")
        return redirect("accounts:department_list")
    return render(request, "form.html", {"form": form, "title": "Edit Department", "cancel_url": "accounts:department_list"})


@staff_required
def department_delete(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == "POST":
        try:
            department.delete()
            messages.success(request, "Department deleted successfully.")
        except ProtectedError:
            messages.error(request, "Cannot delete: this department still has students.")
        return redirect("accounts:department_list")
    return render(request, "confirm_delete.html", {"object": department, "cancel_url": "accounts:department_list"})


# ---------------- Students ----------------

@staff_required
def student_list(request):
    students = StudentProfile.objects.select_related("user", "department").annotate(
        num_complaints=Count("complaints"))
    return render(request, "accounts/student_list.html", {"students": students})


@staff_required
def student_detail(request, pk):
    student = get_object_or_404(StudentProfile, pk=pk)
    complaints = student.complaints.select_related("category")
    return render(request, "accounts/student_detail.html", {"student": student, "complaints": complaints})


@staff_required
def student_update(request, pk):
    student = get_object_or_404(StudentProfile, pk=pk)
    form = StudentProfileForm(request.POST or None, instance=student)
    if form.is_valid():
        form.save()
        messages.success(request, "Student details updated successfully.")
        return redirect("accounts:student_detail", pk=student.pk)
    return render(request, "form.html", {"form": form, "title": f"Edit {student.user.get_full_name()}",
                                         "cancel_url": "accounts:student_list"})


@staff_required
def student_delete(request, pk):
    student = get_object_or_404(StudentProfile, pk=pk)
    if request.method == "POST":
        student.user.delete()   # deleting the login also deletes the profile (CASCADE)
        messages.success(request, "Student account deleted successfully.")
        return redirect("accounts:student_list")
    return render(request, "confirm_delete.html", {"object": student, "cancel_url": "accounts:student_list"})


# ---------------- Staff ----------------

@staff_required
def staff_list(request):
    staff = StaffProfile.objects.select_related("user").annotate(num_assigned=Count("assigned_complaints"))
    return render(request, "accounts/staff_list.html", {"staff": staff})


@staff_required
def staff_detail(request, pk):
    member = get_object_or_404(StaffProfile, pk=pk)
    complaints = member.assigned_complaints.select_related("category", "student__user")
    return render(request, "accounts/staff_detail.html", {"member": member, "complaints": complaints})


@staff_required
def staff_update(request, pk):
    member = get_object_or_404(StaffProfile, pk=pk)
    form = StaffProfileForm(request.POST or None, instance=member)
    if form.is_valid():
        form.save()
        messages.success(request, "Staff details updated successfully.")
        return redirect("accounts:staff_detail", pk=member.pk)
    return render(request, "form.html", {"form": form, "title": f"Edit {member.user.get_full_name()}",
                                         "cancel_url": "accounts:staff_list"})


@staff_required
def staff_delete(request, pk):
    member = get_object_or_404(StaffProfile, pk=pk)
    if request.method == "POST":
        member.user.delete()
        messages.success(request, "Staff account deleted successfully.")
        return redirect("accounts:staff_list")
    return render(request, "confirm_delete.html", {"object": member, "cancel_url": "accounts:staff_list"})
