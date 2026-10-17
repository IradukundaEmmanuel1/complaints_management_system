from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render
from django.utils import timezone

from accounts.models import Faculty, StudentProfile
from complaints.models import Complaint
from complaints.views import visible_complaints


@login_required
def dashboard(request):
    """Dashboard: staff see the whole university, a student sees only his/her complaints."""
    complaints = visible_complaints(request.user)
    total = complaints.count()
    resolved = complaints.filter(status="RESOLVED").count()
    closed = complaints.filter(status__in=["RESOLVED", "REJECTED"])

    # Average number of days to close a complaint
    days = [c.days_open for c in closed]
    avg_days = round(sum(days) / len(days), 1) if days else 0

    open_complaints = complaints.filter(status__in=Complaint.OPEN_STATUSES)
    week_ago = timezone.now() - timedelta(days=Complaint.TARGET_DAYS)

    # Chart data: complaints per category and per status (the database counts them)
    category_counts = complaints.values("category__name").annotate(n=Count("id")).order_by("category__name")
    status_counts = dict(complaints.values_list("status").annotate(n=Count("id")))

    context = {
        "total": total,
        "open_count": open_complaints.count(),
        "resolution_rate": round(resolved * 100 / total, 1) if total else 0,
        "avg_days": avg_days,
        "overdue": open_complaints.filter(created_at__lt=week_ago),
        "unassigned": open_complaints.filter(assigned_to__isnull=True),
        "recent": complaints[:6],
        "category_labels": [row["category__name"] for row in category_counts],
        "category_values": [row["n"] for row in category_counts],
        "status_labels": [label for code, label in Complaint.STATUS_CHOICES],
        "status_values": [status_counts.get(code, 0) for code, label in Complaint.STATUS_CHOICES],
    }
    if request.user.is_staff:
        # Complaints per faculty: follow complaint -> student -> department -> faculty
        context["faculties"] = Faculty.objects.annotate(
            n=Count("departments__students__complaints")).order_by("-n")
        context["total_students"] = StudentProfile.objects.count()
    return render(request, "dashboard.html", context)
