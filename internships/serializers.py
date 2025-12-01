# internships/serializers.py

from rest_framework import serializers
from .models import Internship


# ============================================================
# 1. LIST SERIALIZER (InternshipsListPage.jsx)
# ============================================================

class InternshipListSerializer(serializers.ModelSerializer):
    """
    Used for internship listing cards.
    """

    class Meta:
        model = Internship
        fields = [
            "id",
            "title",
            "company_name",
            "location",
            "duration",
            "stipend",
            "internship_type",
            "category",
            "short_description",
            "skills",
            "created_at",
        ]


# ============================================================
# 2. DETAIL SERIALIZER (InternshipDetailsPage.jsx)
# ============================================================

class InternshipDetailSerializer(serializers.ModelSerializer):
    """
    Used for Internship Details Page.
    Includes full description, responsibilities, skills, eligibility, etc.
    """

    recruiter_id = serializers.IntegerField(source="recruiter.id", read_only=True)

    class Meta:
        model = Internship
        fields = [
            "id",
            "recruiter_id",
            "title",
            "company_name",
            "location",
            "duration",
            "stipend",
            "internship_type",
            "category",
            "short_description",
            "full_description",
            "responsibilities",
            "skills",
            "eligibility",
            "application_deadline",
            "is_active",
            "created_at",
        ]


# ============================================================
# 3. CREATE / UPDATE SERIALIZER (Recruiter Posting)
# ============================================================

class InternshipCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Used for recruiters to create and update internships.
    Includes validation for JSON list fields.
    """

    class Meta:
        model = Internship
        fields = [
            "title",
            "company_name",
            "location",
            "duration",
            "stipend",
            "internship_type",
            "category",
            "short_description",
            "full_description",
            "responsibilities",
            "skills",
            "eligibility",
            "application_deadline",
            "is_active",
        ]

    # ----------------------
    # VALIDATION
    # ----------------------

    def validate(self, attrs):
        """
        Checks JSON list fields are proper lists.
        """

        list_fields = ["responsibilities", "skills"]

        for field in list_fields:
            value = attrs.get(field)
            if value is not None and not isinstance(value, list):
                raise serializers.ValidationError({
                    field: "This field must be a list, e.g. ['Excel','SQL']"
                })

        return attrs

    # ----------------------
    # CREATE / UPDATE
    # ----------------------

    def create(self, validated_data):
        recruiter = self.context["request"].user
        return Internship.objects.create(recruiter=recruiter, **validated_data)

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance
