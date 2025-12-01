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
    """
    Used by recruiters to post new jobs and edit their jobs.
    Handles JSON list fields cleanly.
    """

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

    # ----------------------
    # VALIDATION
    # ----------------------

    def validate(self, attrs):
        """
        Custom validation for JSON list fields + string fields.
        """

        # Ensure JSON list fields are actually lists
        list_fields = ["responsibilities", "requirements", "skills", "eligible_degrees"]

        for field in list_fields:
            value = attrs.get(field)
            if value is not None and not isinstance(value, list):
                raise serializers.ValidationError({
                    field: "This field must be a list, e.g. ['Python','Django']"
                })

        return attrs

    def create(self, validated_data):
        """
        Recruiter is auto-set from view.
        """
        recruiter = self.context["request"].user
        return Job.objects.create(recruiter=recruiter, **validated_data)

    def update(self, instance, validated_data):
        """
        Update job fields cleanly.
        """
        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance
