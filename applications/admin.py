# applications/admin.py

from django.contrib import admin
from .models import JobApplication, InternshipApplication
from .models import SavedJob
from .models import SavedJob, SavedInternship


# ============================================================
# COMMON ADMIN CONFIG (Reusable)
# ============================================================

class BaseApplicationAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "candidate_email",
        "candidate_full_name",
        "get_title",
        "get_company",
        "status",
        "created_at",
        "status_updated_at",
    )

    list_filter = (
        "status",
        "created_at",
        "status_updated_at",
    )

    search_fields = (
        "candidate_email",
        "candidate_full_name",
        "candidate_phone",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "status_updated_at",
        "candidate_email",
        "candidate_full_name",
        "candidate_phone",
        "candidate_location",
        "candidate_resume_url",
        "candidate_skills",
        "candidate_bio",
    )

    ordering = ("-created_at",)

    # -------------------------------------------------------
    # Admin Actions
    # -------------------------------------------------------

    actions = ["mark_viewed", "mark_shortlisted", "mark_rejected"]

    def mark_viewed(self, request, queryset):
        updated = queryset.update(status="viewed")
        self.message_user(request, f"{updated} application(s) marked as Viewed.")
    mark_viewed.short_description = "Mark as Viewed"

    def mark_shortlisted(self, request, queryset):
        updated = queryset.update(status="shortlisted")
        self.message_user(request, f"{updated} application(s) marked as Shortlisted.")
    mark_shortlisted.short_description = "Mark as Shortlisted"

    def mark_rejected(self, request, queryset):
        updated = queryset.update(status="rejected")
        self.message_user(request, f"{updated} application(s) marked as Rejected.")
    mark_rejected.short_description = "Mark as Rejected"


# ============================================================
# JOB APPLICATION ADMIN
# ============================================================

@admin.register(JobApplication)
class JobApplicationAdmin(BaseApplicationAdmin):

    def get_title(self, obj):
        return obj.job.title
    get_title.short_description = "Job Title"

    def get_company(self, obj):
        return obj.job.company_name
    get_company.short_description = "Company"


# ============================================================
# INTERNSHIP APPLICATION ADMIN
# ============================================================

@admin.register(InternshipApplication)
class InternshipApplicationAdmin(BaseApplicationAdmin):

    def get_title(self, obj):
        return obj.internship.title
    get_title.short_description = "Internship Title"

    def get_company(self, obj):
        return obj.internship.company_name
    get_company.short_description = "Company"

@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ("user", "job", "saved_on")
    search_fields = ("user__email", "job__title")
    list_filter = ("saved_on",)
    readonly_fields = ("saved_on",)

@admin.register(SavedInternship)
class SavedInternshipAdmin(admin.ModelAdmin):
    list_display = ("user", "internship", "saved_on")
    search_fields = ("user__email", "internship__title")
    list_filter = ("saved_on",)
    readonly_fields = ("saved_on",)
