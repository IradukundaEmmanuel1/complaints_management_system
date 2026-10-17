from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, ProtectedError, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.permissions import staff_required
from .forms import CategoryForm, ComplaintForm, ComplaintStaffForm, ResponseForm
from .models import Category, Complaint


def visible_complaints(user):
    """Staff see every complaint. A student sees ONLY his/her own complaints."""
    complaints = Complaint.objects.select_related("student__user", "category", "assigned_to__user")
    if user.is_staff:
        return complaints
    if hasattr(user, "student_profile"):
        return complaints.filter(student=user.student_profile)
    return complaints.none()


def can_student_change(user, complaint):
    """A student may edit/delete only his/her own complaint, and only before staff start on it."""
    return (hasattr(user, "student_profile") and complaint.student == user.student_profile
            and complaint.status == "SUBMITTED")


# ---------------- Complaints ----------------

@login_required
def complaint_list(request):
    complaints = visible_complaints(request.user)
    query = request.GET.get("q", "")
    if query:   # search box: reference, title or student name
        complaints = complaints.filter(Q(reference__icontains=query) | Q(title__icontains=query)
                                       | Q(student__user__first_name__icontains=query)
                                       | Q(student__user__last_name__icontains=query))
    return render(request, "complaints/complaint_list.html", {"complaints": complaints, "query": query})


@login_required
def complaints_by_status(request, status):
    # Dynamic URL with a text parameter: /complaints/status/in_review/
    status = status.upper()
    labels = dict(Complaint.STATUS_CHOICES)
    if status not in labels:
        raise Http404("Unknown status")
    complaints = visible_complaints(request.user).filter(status=status)
    return render(request, "complaints/complaint_list.html",
                  {"complaints": complaints, "status_label": labels[status]})


@login_required
def complaint_detail(request, pk):
    complaint = get_object_or_404(visible_complaints(request.user), pk=pk)
    form = ResponseForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        response = form.save(commit=False)
        response.complaint = complaint
        response.author = request.user
        response.save()
        messages.success(request, "Your reply was added.")
        return redirect("complaints:complaint_detail", pk=complaint.pk)
    return render(request, "complaints/complaint_detail.html", {
        "complaint": complaint, "responses": complaint.responses.select_related("author"),
        "form": form, "can_change": request.user.is_staff or can_student_change(request.user, complaint),
    })


@login_required
def complaint_create(request):
    if not hasattr(request.user, "student_profile"):
        raise PermissionDenied   # only students submit complaints
    student = request.user.student_profile
    form = ComplaintForm(request.POST or None, student=student)
    if form.is_valid():
        complaint = form.save(commit=False)
        complaint.student = student
        complaint.assigned_to = complaint.category.default_handler   # send it to the right office
        complaint.save()
        form.save_m2m()   # save the tags (ManyToMany) after the complaint exists
        messages.success(request, f"Complaint {complaint.reference} submitted. You will be notified of the response.")
        return redirect("complaints:complaint_detail", pk=complaint.pk)
    return render(request, "form.html", {"form": form, "title": "Submit a Complaint",
                                         "cancel_url": "complaints:complaint_list"})


@login_required
def complaint_update(request, pk):
    complaint = get_object_or_404(visible_complaints(request.user), pk=pk)
    if request.user.is_staff:
        form = ComplaintStaffForm(request.POST or None, instance=complaint)
        title = f"Manage {complaint.reference}"
    elif can_student_change(request.user, complaint):
        form = ComplaintForm(request.POST or None, instance=complaint, student=complaint.student)
        title = f"Edit {complaint.reference}"
    else:
        messages.error(request, "This complaint is already being handled and can no longer be edited.")
        return redirect("complaints:complaint_detail", pk=complaint.pk)

    if form.is_valid():
        complaint = form.save(commit=False)
        # Record the date when the complaint is closed
        complaint.resolved_at = timezone.now() if complaint.status in ("RESOLVED", "REJECTED") else None
        complaint.save()
        form.save_m2m()
        messages.success(request, f"Complaint {complaint.reference} updated successfully.")
        return redirect("complaints:complaint_detail", pk=complaint.pk)
    return render(request, "form.html", {"form": form, "title": title, "cancel_url": "complaints:complaint_list"})


@login_required
def complaint_delete(request, pk):
    complaint = get_object_or_404(visible_complaints(request.user), pk=pk)
    if not (request.user.is_staff or can_student_change(request.user, complaint)):
        messages.error(request, "This complaint is already being handled and can no longer be deleted.")
        return redirect("complaints:complaint_detail", pk=complaint.pk)
    if request.method == "POST":
        complaint.delete()
        messages.success(request, "Complaint deleted successfully.")
        return redirect("complaints:complaint_list")
    return render(request, "confirm_delete.html", {"object": complaint, "cancel_url": "complaints:complaint_list"})


# ---------------- Categories ----------------

@staff_required
def category_list(request):
    categories = Category.objects.select_related("default_handler__user").annotate(
        num_complaints=Count("complaints"),
        num_open=Count("complaints", filter=Q(complaints__status__in=Complaint.OPEN_STATUSES)))
    return render(request, "complaints/category_list.html", {"categories": categories})


@staff_required
def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    complaints = category.complaints.select_related("student__user")
    return render(request, "complaints/category_detail.html", {"category": category, "complaints": complaints})


@staff_required
def category_create(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Category added successfully.")
        return redirect("complaints:category_list")
    return render(request, "form.html", {"form": form, "title": "Add Category", "cancel_url": "complaints:category_list"})


@staff_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=category)
    if form.is_valid():
        form.save()
        messages.success(request, "Category updated successfully.")
        return redirect("complaints:category_list")
    return render(request, "form.html", {"form": form, "title": "Edit Category", "cancel_url": "complaints:category_list"})


@staff_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        try:
            category.delete()
            messages.success(request, "Category deleted successfully.")
        except ProtectedError:
            messages.error(request, "Cannot delete: there are complaints in this category.")
        return redirect("complaints:category_list")
    return render(request, "confirm_delete.html", {"object": category, "cancel_url": "complaints:category_list"})
