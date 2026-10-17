import re

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Department, Faculty, StaffProfile, StudentProfile


class StyledModelForm(forms.ModelForm):
    """Adds the Bootstrap 'form-control' class to every field (AdminLTE style)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs["class"] = "form-control"


class FacultyForm(StyledModelForm):
    class Meta:
        model = Faculty
        fields = ["code", "name", "campus"]

    def clean_code(self):
        # Validation: 2 to 5 capital letters, e.g. IT, BA
        code = self.cleaned_data["code"].strip().upper()
        if not re.fullmatch(r"[A-Z]{2,5}", code):
            raise forms.ValidationError("Use 2 to 5 letters, e.g. IT.")
        return code


class DepartmentForm(StyledModelForm):
    class Meta:
        model = Department
        fields = ["name", "faculty"]


class StudentRegistrationForm(UserCreationForm):
    """Sign-up form: creates the login account (User) AND the StudentProfile."""
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField()
    reg_number = forms.CharField(label="Registration number", max_length=12)
    department = forms.ModelChoiceField(queryset=Department.objects.select_related("faculty"))
    year_of_study = forms.IntegerField(min_value=1, max_value=5)
    phone = forms.CharField(max_length=10)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["username", "first_name", "last_name", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_reg_number(self):
        # Validation: starts with the 4-digit year, e.g. 20251SE014
        reg = self.cleaned_data["reg_number"].strip().upper()
        if not re.fullmatch(r"20\d{2}[0-9A-Z]{4,8}", reg):
            raise forms.ValidationError("Start with the year, e.g. 20251SE014.")
        if StudentProfile.objects.filter(reg_number=reg).exists():
            raise forms.ValidationError("This registration number is already registered.")
        return reg

    def clean_phone(self):
        # Validation: Rwandan mobile number, 10 digits starting with 07
        phone = self.cleaned_data["phone"].replace(" ", "")
        if not re.fullmatch(r"07\d{8}", phone):
            raise forms.ValidationError("Enter a 10-digit number starting with 07, e.g. 0788123456.")
        return phone

    def save(self, commit=True):
        user = super().save()   # creates the User with a hashed password
        StudentProfile.objects.create(
            user=user, reg_number=self.cleaned_data["reg_number"],
            department=self.cleaned_data["department"],
            year_of_study=self.cleaned_data["year_of_study"], phone=self.cleaned_data["phone"])
        return user


class StudentProfileForm(StyledModelForm):
    """Used by staff to correct a student's academic details."""
    class Meta:
        model = StudentProfile
        fields = ["reg_number", "department", "year_of_study", "phone"]

    def clean_phone(self):
        phone = self.cleaned_data["phone"].replace(" ", "")
        if not re.fullmatch(r"07\d{8}", phone):
            raise forms.ValidationError("Enter a 10-digit number starting with 07, e.g. 0788123456.")
        return phone


class StaffProfileForm(StyledModelForm):
    class Meta:
        model = StaffProfile
        fields = ["staff_number", "position", "office"]
