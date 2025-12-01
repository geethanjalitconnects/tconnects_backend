# profiles/admin.py

from django.contrib import admin
from .models import (
    CandidateProfile,
    RecruiterBasicProfile,
    CompanyProfile,
    FreelancerBasicInfo,
    FreelancerProfessionalDetails,
    FreelancerEducation,
    FreelancerAvailability,
    FreelancerPaymentMethod,
    FreelancerSocialLinks,
)


# ============================================================
# Candidate Profile
# ============================================================

@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "phone_number",
        "location",
        "experience_level",
        "updated_at",
    )
    list_filter = ("experience_level", "updated_at")
    search_fields = ("user__email", "user__full_name", "phone_number", "location")
    readonly_fields = ("updated_at",)


# ============================================================
# Recruiter Basic Profile
# ============================================================

@admin.register(RecruiterBasicProfile)
class RecruiterBasicProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "company_email",
        "phone_number",
        "position_in_company",
        "updated_at",
    )
    search_fields = ("user__email", "company_email", "position_in_company")
    readonly_fields = ("updated_at",)


# ============================================================
# Company Profile
# ============================================================

@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = (
        "company_name",
        "industry_category",
        "company_size",
        "company_location",
        "company_website",
        "updated_at",
    )
    search_fields = ("company_name", "industry_category", "company_location")
    list_filter = ("industry_category", "company_size")
    readonly_fields = ("created_at", "updated_at")


# ============================================================
# Freelancer: Education inline
# ============================================================

class FreelancerEducationInline(admin.TabularInline):
    model = FreelancerEducation
    extra = 1
    readonly_fields = ("created_at",)


# ============================================================
# Freelancer Basic Info
# ============================================================

@admin.register(FreelancerBasicInfo)
class FreelancerBasicInfoAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "full_name",
        "phone_number",
        "location",
        "created_at",
        "updated_at",
    )
    inlines = [FreelancerEducationInline]
    search_fields = ("user__email", "full_name", "location")
    readonly_fields = ("created_at", "updated_at")


# ============================================================
# Freelancer Professional Details
# ============================================================

@admin.register(FreelancerProfessionalDetails)
class FreelancerProfessionalDetailsAdmin(admin.ModelAdmin):
    list_display = (
        "freelancer",
        "area_of_expertise",
        "years_of_experience",
        "job_category",
        "updated_at",
    )
    search_fields = ("freelancer__user__email", "area_of_expertise", "job_category")
    readonly_fields = ("updated_at",)


# ============================================================
# Freelancer Availability
# ============================================================

@admin.register(FreelancerAvailability)
class FreelancerAvailabilityAdmin(admin.ModelAdmin):
    list_display = (
        "freelancer",
        "is_available",
        "is_occupied",
        "available_from",
        "available_to",
        "time_zone",
        "updated_at",
    )
    search_fields = ("freelancer__user__email", "time_zone")
    readonly_fields = ("updated_at",)


# ============================================================
# Freelancer Payment Methods
# ============================================================

@admin.register(FreelancerPaymentMethod)
class FreelancerPaymentMethodAdmin(admin.ModelAdmin):
    list_display = (
        "freelancer",
        "payment_type",
        "upi_id",
        "account_holder_name",
        "created_at",
    )
    list_filter = ("payment_type",)
    search_fields = ("freelancer__user__email", "upi_id", "account_holder_name")
    readonly_fields = ("created_at",)


# ============================================================
# Freelancer Social Links
# ============================================================

@admin.register(FreelancerSocialLinks)
class FreelancerSocialLinksAdmin(admin.ModelAdmin):
    list_display = (
        "freelancer",
        "linkedin_url",
        "github_url",
        "portfolio_url",
        "rating",
        "updated_at",
    )
    search_fields = (
        "freelancer__user__email",
        "linkedin_url",
        "github_url",
        "portfolio_url",
    )
    readonly_fields = ("updated_at",)
