# AUCA Students' Complaints Management System:

A web application where Adventist University of Central Africa (AUCA) students submit and follow
complaints, and AUCA staff assign, answer and resolve them. Built with Django and AdminLTE 3.

**Group members:** IRADUKUNDA Emmanuel (20251MBI047), Aimable HABIMANA 
(20251MBI055), Dushimirimana Daniel (20251MBI028)


## How to run (windows)

```bash
cd complaints_system
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
python manage.py runserver
```

On Windows use `venv\Scripts\activate`. Then open http://127.0.0.1:8000/

The database (`db.sqlite3`) is already migrated and contains a small set of sample data.
To rebuild it: `python3 manage.py migrate` then `python3 manage.py seed_data`.

## Login credentials

| Role | Username | Password |
|---|---|---|
| Superuser (Django Admin) | `admin` | `Admin@2026` |
| Staff (Academic Registrar) | `guwimana` | `Staff@2026` |
| Staff (Dean of Students, ICT Support) | `pniyonzima`, `emugisha` | `Staff@2026` |
| Students | `aline`, `kevin`, `sandrine`, `olivier`,`emmanuel`,`aimable`,`daniel` | `Kigali@2026` |

New students can create an account at `/register/`.

## Main pages

| URL | Page | Who |
|---|---|---|
| `/` | Dashboard | Everyone (own data for students) |
| `/register/` | Student sign-up | Public |
| `/complaints/` | Complaints (search, filters, View/Edit/Delete) | Students: own; staff: all |
| `/complaints/new/` | Submit a complaint | Students |
| `/complaints/status/<status>/` | Complaints by status (dynamic text URL) | Everyone |
| `/complaints/categories/` | Categories (CRUD) | Staff |
| `/accounts/faculties/`, `/accounts/departments/` | University structure (CRUD) | Staff |
| `/accounts/students/`, `/accounts/staff/` | People | Staff |
| `/admin/` | Django Admin | Superuser |

## Project structure

```
complaints_system/   project settings, project URLs, dashboard view
complaints/          App 1: Category, Tag, Complaint, Response + seed_data command
accounts/            App 2: Faculty, Department, StudentProfile, StaffProfile, sign-up, staff_required
templates/           shared templates (AdminLTE layout, dashboard, forms, login, sign-up, 403)
static/adminlte/     the complete AdminLTE 3.2 bundle
static/css/theme.css our own colours (navy blue and amber)
```
