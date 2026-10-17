from django import forms

from accounts.forms import StyledModelForm
from .models import Category, Complaint, Response


class CategoryForm(StyledModelForm):
    class Meta:
        model = Category
        fields = ["name", "description", "default_handler"]


class ComplaintForm(StyledModelForm):
    """Form used by a STUDENT to submit or edit a complaint."""

    class Meta:
        model = Complaint
        fields = ["category", "title", "description", "priority", "tags"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "tags": forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, student=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.student = student

    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        if len(title) < 10:
            raise forms.ValidationError("Please give a clearer title (at least 10 characters).")
        return title

    def clean_description(self):
        text = self.cleaned_data["description"].strip()
        if len(text.split()) < 8:
            raise forms.ValidationError("Please explain the problem in at least 8 words.")
        return text

    def clean_tags(self):
        tags = self.cleaned_data["tags"]
        if len(tags) > 3:
            raise forms.ValidationError("Choose at most 3 tags.")
        return tags

    def clean(self):
        cleaned = super().clean()
        title, category = cleaned.get("title"), cleaned.get("category")
        # Business rule: the same student cannot open the same complaint twice
        if self.student and title and category:
            duplicate = Complaint.objects.filter(
                student=self.student, category=category, title__iexact=title,
                status__in=Complaint.OPEN_STATUSES).exclude(pk=self.instance.pk)
            if duplicate.exists():
                raise forms.ValidationError("You already have an open complaint with this title in this category.")
        return cleaned


class ComplaintStaffForm(StyledModelForm):
    """Form used by STAFF to assign, change the status and write the resolution."""

    class Meta:
        model = Complaint
        fields = ["category", "priority", "status", "assigned_to", "resolution"]
        widgets = {"resolution": forms.Textarea(attrs={"rows": 3})}

    def clean(self):
        cleaned = super().clean()
        status, assigned, resolution = cleaned.get("status"), cleaned.get("assigned_to"), cleaned.get("resolution")
        if status == "IN_REVIEW" and not assigned:
            self.add_error("assigned_to", "Assign a staff member before putting the complaint in review.")
        if status in ("RESOLVED", "REJECTED") and not (resolution or "").strip():
            self.add_error("resolution", "Explain how the complaint was resolved, or why it was rejected.")
        return cleaned


class ResponseForm(StyledModelForm):
    class Meta:
        model = Response
        fields = ["message"]
        widgets = {"message": forms.Textarea(attrs={"rows": 3, "placeholder": "Write a reply..."})}

    def clean_message(self):
        message = self.cleaned_data["message"].strip()
        if len(message) < 5:
            raise forms.ValidationError("The message is too short.")
        return message
