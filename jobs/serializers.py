# jobs/serializers.py

from rest_framework import serializers
from .models import Job


# ============================================================
# 1. LIST SERIALIZER (For JobsListPage.jsx)
# ============================================================

class JobListSerializer(serializers.ModelSerializer):
    """
    Used for job cards listing.
    Shows only the fields needed in JobsListPage.jsx.
    """

    class Meta:
        model = Job
        fields = [
            "id",
            "title",
            "company_name",
            "location",
            "experience_range",
            "salary_range",
            "employment_type",
            "category",
            "short_description",
            "skills",
            "created_at",
        ]


# ============================================================
# 2. DETAIL SERIALIZER (For JobDetailsPage.jsx)
# ============================================================

class JobDetailSerializer(serializers.ModelSerializer):
    """
    Used for Job Details Page.
    Includes full description, responsibilities, requirements, eligible degrees, etc.
    """

    recruiter_id = serializers.IntegerField(source="recruiter.id", read_only=True)

    class Meta:
        model = Job
        fields = [
            "id",
            "recruiter_id",
            "title",
            "company_name",
            "location",
            "experience_range",
            "salary_range",
            "employment_type",
            "category",
            "short_description",
            "full_description",
            "responsibilities",
            "requirements",
            "skills",
            "eligible_degrees",
            "application_deadline",
            "is_active",
            "created_at",
        ]


# ============================================================
# 3. CREATE / UPDATE SERIALIZER (Recruiter Dashboard)
# ============================================================

class JobCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            "title",
            "company_name",
            "location",
            "experience_range",
            "salary_range",
            "employment_type",
            "category",
            "short_description",
            "full_description",
            "responsibilities",
            "requirements",
            "skills",
            "eligible_degrees",
            "application_deadline",
            "is_active",
        ]
        extra_kwargs = {
            "company_name": {"required": False},
            "short_description": {"required": False},
            "requirements": {"required": False},
            "eligible_degrees": {"required": False},
        }

    def validate(self, attrs):
        list_fields = ["responsibilities", "requirements", "skills", "eligible_degrees"]

        for field in list_fields:
            value = attrs.get(field)
            if value is not None and not isinstance(value, list):
                raise serializers.ValidationError({
                    field: "This field must be a list."
                })

        return attrs

    def create(self, validated_data):
        recruiter = self.context["request"].user

        # Auto-fill company name from Recruiter's Company Profile
        company = getattr(recruiter, "company_profile", None)
        validated_data["company_name"] = company.company_name if company else "Unknown Company"

        # Auto-generate short description
        full_desc = validated_data.get("full_description", "")
        validated_data["short_description"] = full_desc[:120]

        return Job.objects.create(recruiter=recruiter, **validated_data)
