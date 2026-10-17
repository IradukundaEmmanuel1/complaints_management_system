from datetime import date

from django.conf import settings
from django.db import models

from accounts.models import StaffProfile, StudentProfile


class Category(models.Model):
    """Type of complaint, e.g. Academic, Finance. Each category has a default handler."""
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=200)
    default_handler = models.ForeignKey(StaffProfile, on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name="handled_categories")

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Short label to group complaints, e.g. Urgent, Marks, Wi-Fi."""
    name = models.CharField(max_length=30, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Complaint(models.Model):
    """A complaint submitted by ONE student, in ONE category, handled by ONE staff member."""
    PRIORITY_CHOICES = [("LOW", "Low"), ("MEDIUM", "Medium"), ("HIGH", "High")]
    STATUS_CHOICES = [("SUBMITTED", "Submitted"), ("IN_REVIEW", "In review"),
                      ("RESOLVED", "Resolved"), ("REJECTED", "Rejected")]
    OPEN_STATUSES = ["SUBMITTED", "IN_REVIEW"]
    TARGET_DAYS = 7   # the university aims to answer within 7 days

    reference = models.CharField(max_length=15, unique=True, blank=True, editable=False)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="complaints")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="complaints")
    # Many-to-many: a complaint can have several tags, a tag is used by many complaints
    tags = models.ManyToManyField(Tag, related_name="complaints", blank=True)
    title = models.CharField(max_length=150)
    description = models.TextField()
    priority = models.CharField(max_length=6, choices=PRIORITY_CHOICES, default="MEDIUM")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="SUBMITTED")
    assigned_to = models.ForeignKey(StaffProfile, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name="assigned_complaints")
    resolution = models.TextField("Resolution / reason", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.reference} - {self.title}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Give every new complaint a reference number like CMP-2026-0007
        if not self.reference:
            self.reference = f"CMP-{self.created_at.year}-{self.pk:04d}"
            super().save(update_fields=["reference"])

    @property
    def is_open(self):
        return self.status in self.OPEN_STATUSES

    @property
    def days_open(self):
        end = self.resolved_at.date() if self.resolved_at else date.today()
        return (end - self.created_at.date()).days

    @property
    def is_overdue(self):
        return self.is_open and self.days_open > self.TARGET_DAYS


class Response(models.Model):
    """A message in the complaint's conversation, written by a student or a staff member."""
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name="responses")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="responses")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Response to {self.complaint.reference} by {self.author.get_full_name()}"
