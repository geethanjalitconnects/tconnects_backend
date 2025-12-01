# internships/admin.py

from django.contrib import admin
from .models import Internship


@admin.register(Internship)
class InternshipAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "company_name",
        "location",
        "duration",
        "stipend",
        "internship_type",
        "category",
        "is_active",
        "created_at",
        "recruiter",
    )

    list_filter = (
        "internship_type",
        "category",
        "location",
        "is_active",
        "created_at",
    )

    search_fields = (
        "title",
        "company_name",
        "location",
        "recruiter__email",
    )

    readonly_fields = ("created_at", "updated_at")

    ordering = ("-created_at",)
