"""Project-level URLs: they send each request to the right app."""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from accounts import views as account_views
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),                    # Dashboard home
    path("complaints/", include("complaints.urls")),                # App 1
    path("accounts/", include("accounts.urls")),                    # App 2
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("register/", account_views.register, name="register"),
    path("admin/", admin.site.urls),                                 # Django Admin
]
