from django.contrib import admin

from .models import Category, Complaint, Response, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "default_handler")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)


class ResponseInline(admin.TabularInline):
    model = Response
    extra = 0


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ("reference", "title", "student", "category", "priority", "status", "assigned_to", "created_at")
    list_filter = ("status", "priority", "category")
    search_fields = ("reference", "title")
    filter_horizontal = ("tags",)
    inlines = [ResponseInline]
