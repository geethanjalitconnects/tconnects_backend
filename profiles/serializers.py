# profiles/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
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

User = get_user_model()


# ============================================================
# USER SERIALIZER (for nested return)
# ============================================================

class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "full_name", "role"]
        read_only_fields = fields


# ============================================================
# CANDIDATE PROFILE SERIALIZERS
# ============================================================

class CandidateProfileSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)

    class Meta:
        model = CandidateProfile
        fields = [
            "user",
            "phone_number",
            "location",
            "experience_level",
            "skills",
            "bio",
            "resume",
            "profile_picture",
            "updated_at",
        ]
        read_only_fields = ["updated_at"]


class CandidateResumeUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateProfile
        fields = ["resume"]


class CandidateProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateProfile
        fields = ["profile_picture"]


# ============================================================
# RECRUITER BASIC PROFILE SERIALIZER
# ============================================================

class RecruiterBasicProfileSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)

    class Meta:
        model = RecruiterBasicProfile
        fields = [
            "user",
            "full_name",
            "company_email",
            "phone_number",
            "position_in_company",
            "linkedin_profile",
            "updated_at",
        ]
        read_only_fields = ["updated_at"]


# ============================================================
# COMPANY PROFILE SERIALIZER
# ============================================================

class CompanyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyProfile
        fields = [
            "company_name",
            "industry_category",
            "company_size",
            "company_location",
            "company_website",
            "about_company",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]





# -----------------------------------------------------------
# BASIC INFO
# -----------------------------------------------------------
class FreelancerBasicInfoSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)

    class Meta:
        model = FreelancerBasicInfo
        fields = [
            "user",
            "full_name",
            "phone_number",
            "location",
            "languages_known",
            "profile_picture",
            "is_published",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


# ----------------------------------------------------
# PROFESSIONAL DETAILS
# ----------------------------------------------------
class FreelancerProfessionalDetailsSerializer(serializers.ModelSerializer):
    expertise = serializers.CharField(source="area_of_expertise", allow_blank=True, required=False)
    experience = serializers.IntegerField(source="years_of_experience", required=False, allow_null=True)
    categories = serializers.CharField(source="job_category", allow_blank=True, required=False)
    bio = serializers.CharField(source="professional_bio", allow_blank=True, required=False)

    class Meta:
        model = FreelancerProfessionalDetails
        fields = [
            "expertise",
            "experience",
            "categories",
            "bio",
            "updated_at",
        ]
        read_only_fields = ["updated_at"]
    
    def to_internal_value(self, data):
        """Handle both aliased and raw field names for PATCH/POST"""
        # Map raw field names to aliased field names if present
        if "area_of_expertise" in data:
            data["expertise"] = data.pop("area_of_expertise")
        if "years_of_experience" in data:
            data["experience"] = data.pop("years_of_experience")
        if "job_category" in data:
            data["categories"] = data.pop("job_category")
        if "professional_bio" in data:
            data["bio"] = data.pop("professional_bio")
        
        return super().to_internal_value(data)


# ----------------------------------------------------
# EDUCATION (FIXED — removed updated_at)
# ----------------------------------------------------
class FreelancerEducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreelancerEducation
        fields = [
            "id",
            "degree",
            "institution",
            "start_year",
            "end_year",
            "description",
            "created_at",
        ]
        read_only_fields = ["created_at"]



# ----------------------------------------------------
# AVAILABILITY
# ----------------------------------------------------
class FreelancerAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = FreelancerAvailability
        fields = [
            "is_available",
            "is_occupied",
            "available_from",
            "available_to",
            "time_zone",
            "available_days",
            "updated_at",
        ]
        read_only_fields = ["updated_at"]



# ----------------------------------------------------
# PAYMENT METHODS
# ----------------------------------------------------
class FreelancerPaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreelancerPaymentMethod
        fields = [
            "id",
            "payment_type",
            "upi_id",
            "account_number",
            "ifsc_code",
            "bank_name",
            "updated_at",
        ]
        read_only_fields = ["updated_at"]


# ----------------------------------------------------
# SOCIAL LINKS
# ----------------------------------------------------
class FreelancerSocialLinksSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreelancerSocialLinks
        fields = [
            "linkedin_url",
            "github_url",
            "portfolio_url",
            "rating",
            "ratings",
            "badges",
            "updated_at",
        ]
        read_only_fields = ["updated_at"]