from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Faculty(models.Model):
    """An AUCA faculty, e.g. Information Technology (Gishushu campus)."""
    CAMPUS_CHOICES = [("MASORO", "Masoro campus"), ("GISHUSHU", "Gishushu campus"),
                      ("NGOMA", "Ngoma campus")]

    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=100, unique=True)
    campus = models.CharField(max_length=10, choices=CAMPUS_CHOICES)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "faculties"

    def __str__(self):
        return f"Faculty of {self.name}"


class Department(models.Model):
    """A department belongs to ONE faculty (ForeignKey)."""
    name = models.CharField(max_length=100)
    faculty = models.ForeignKey(Faculty, on_delete=models.PROTECT, related_name="departments")

    class Meta:
        ordering = ["faculty__name", "name"]
        constraints = [models.UniqueConstraint(fields=["name", "faculty"], name="unique_department_per_faculty")]

    def __str__(self):
        return self.name


class StudentProfile(models.Model):
    """Extra information for a student. One login account = one student (OneToOne)."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name="student_profile")
    reg_number = models.CharField("Registration number", max_length=12, unique=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="students")
    year_of_study = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)])
    phone = models.CharField(max_length=10)

    class Meta:
        ordering = ["reg_number"]

    def __str__(self):
        return f"{self.reg_number} - {self.user.get_full_name()}"


class StaffProfile(models.Model):
    """A staff member who handles complaints. One login account = one staff member (OneToOne)."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name="staff_profile")
    staff_number = models.CharField(max_length=10, unique=True)
    position = models.CharField(max_length=100)
    office = models.CharField(max_length=100)

    class Meta:
        ordering = ["staff_number"]

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.position})"
