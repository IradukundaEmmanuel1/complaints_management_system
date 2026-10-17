"""Fill the database with a small set of sample data:  python manage.py seed_data"""
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Department, Faculty, StaffProfile, StudentProfile
from complaints.models import Category, Complaint, Response, Tag


class Command(BaseCommand):
    help = "Create sample faculties, departments, users, categories and complaints."

    def handle(self, *args, **options):
        # Faculties and departments (AUCA)
        it = Faculty.objects.get_or_create(code="IT", defaults={"name": "Information Technology", "campus": "GISHUSHU"})[0]
        ba = Faculty.objects.get_or_create(code="BA", defaults={"name": "Business Administration", "campus": "MASORO"})[0]
        se = Department.objects.get_or_create(name="Software Engineering", faculty=it)[0]
        ncs = Department.objects.get_or_create(name="Networks and Communication Systems", faculty=it)[0]
        acc = Department.objects.get_or_create(name="Accounting", faculty=ba)[0]

        # Superuser
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@auca.ac.rw", "Admin@2026", first_name="System", last_name="Administrator")

        # Staff who handle complaints (is_staff=True)
        staff = {}
        for username, first, last, number, position, office in [
            ("pniyonzima", "Patrick", "Niyonzima", "STF001", "Dean of Students", "Student Affairs, Masoro"),
            ("guwimana", "Grace", "Uwimana", "STF002", "Academic Registrar", "Registrar's Office, Masoro"),
            ("emugisha", "Eric", "Mugisha", "STF003", "ICT Support Officer", "ICT Office, Gishushu"),
        ]:
            user, created = User.objects.get_or_create(username=username, defaults={
                "first_name": first, "last_name": last, "email": f"{username}@auca.ac.rw", "is_staff": True})
            if created:
                user.set_password("Staff@2026")
                user.save()
            staff[username] = StaffProfile.objects.get_or_create(user=user, defaults={
                "staff_number": number, "position": position, "office": office})[0]

        # Students
        students = {}
        for username, first, last, reg, dept, year, phone in [
            ("aline", "Aline", "Mutoni", "20251SE014", se, 2, "0788112233"),
            ("kevin", "Kevin", "Ishimwe", "20251NCS007", ncs, 3, "0722445566"),
            ("sandrine", "Sandrine", "Uwase", "20251ACC021", acc, 1, "0783667788"),
            ("olivier", "Olivier", "Nshimiyimana", "20241SE031", se, 3, "0735889900"),
        ]:
            user, created = User.objects.get_or_create(username=username, defaults={
                "first_name": first, "last_name": last, "email": f"{username}.{last.lower()}@student.auca.ac.rw"})
            if created:
                user.set_password("Student@2026")
                user.save()
            students[username] = StudentProfile.objects.get_or_create(user=user, defaults={
                "reg_number": reg, "department": dept, "year_of_study": year, "phone": phone})[0]

        # Categories (each one goes to the right office by default)
        categories = {}
        for name, description, handler in [
            ("Academic", "Marks, exams, timetable and lecturers", "guwimana"),
            ("Finance", "Tuition fees, payments and receipts", "pniyonzima"),
            ("ICT Services", "Internet, Wi-Fi, e-learning and student portal", "emugisha"),
            ("Facilities", "Classrooms, library and campus buildings", "pniyonzima"),
        ]:
            categories[name] = Category.objects.get_or_create(name=name, defaults={
                "description": description, "default_handler": staff[handler]})[0]

        tags = {name: Tag.objects.get_or_create(name=name)[0]
                for name in ["Urgent", "Marks", "Exams", "Fees", "Wi-Fi", "Library"]}

        # Complaints: (student, category, title, description, priority, status, staff, days ago, tags, resolution)
        if not Complaint.objects.exists():
            now = timezone.now()
            data = [
                ("aline", "Academic", "Missing CAT marks for Web Technologies",
                 "My CAT marks for Web Technologies and API Services are not showing on the student portal, but other students in my class can see theirs.",
                 "HIGH", "IN_REVIEW", "guwimana", 4, ["Marks", "Urgent"], ""),
                ("kevin", "ICT Services", "Wi-Fi not working in Gishushu library",
                 "Since Monday the Wi-Fi in the Gishushu campus library disconnects every few minutes, so we cannot access e-learning materials.",
                 "MEDIUM", "SUBMITTED", "emugisha", 9, ["Wi-Fi", "Library"], ""),
                ("sandrine", "Finance", "Fee payment not shown on my account",
                 "I paid my tuition fees at the bank two weeks ago but the payment is still not shown on my student account, so I cannot see my results.",
                 "HIGH", "RESOLVED", "pniyonzima", 12, ["Fees"], "The bank slip was verified and the payment was added to the student account."),
                ("olivier", "Academic", "Exam timetable clash for two courses",
                 "Two of my final exams, Database Systems and Computer Networks, are scheduled on the same day at the same time.",
                 "MEDIUM", "RESOLVED", "guwimana", 20, ["Exams"], "The Computer Networks exam was moved to the following day for the affected students."),
                ("aline", "Facilities", "Broken projector in classroom",
                 "The projector in our classroom has not worked for a week, and lecturers cannot show their slides during class.",
                 "LOW", "SUBMITTED", "pniyonzima", 2, [], ""),
            ]
            for user, cat, title, desc, priority, status, handler, days, tag_names, resolution in data:
                c = Complaint.objects.create(student=students[user], category=categories[cat], title=title,
                                             description=desc, priority=priority, status=status,
                                             assigned_to=staff[handler], resolution=resolution)
                c.tags.set([tags[t] for t in tag_names])
                created = now - timedelta(days=days)
                resolved = created + timedelta(days=3) if status == "RESOLVED" else None
                Complaint.objects.filter(pk=c.pk).update(created_at=created, resolved_at=resolved)

            first = Complaint.objects.get(title__startswith="Missing CAT")
            Response.objects.create(complaint=first, author=staff["guwimana"].user,
                                    message="Thank you, Aline. We have contacted the lecturer to upload the missing marks.")
            Response.objects.create(complaint=first, author=students["aline"].user,
                                    message="Thank you. Please let me know when they are available.")

        self.stdout.write(self.style.SUCCESS(
            f"Done: {Faculty.objects.count()} faculties, {Department.objects.count()} departments, "
            f"{StaffProfile.objects.count()} staff, {StudentProfile.objects.count()} students, "
            f"{Category.objects.count()} categories, {Complaint.objects.count()} complaints."))
