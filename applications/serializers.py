from rest_framework import serializers
from django.utils import timezone

from .models import JobApplication, InternshipApplication, SavedJob, SavedInternship
from profiles.models import CandidateProfile
from jobs.models import Job
from internships.models import Internship


# ============================================================
# UTIL — Fetch Candidate Snapshot
# ============================================================

def build_candidate_snapshot(user):
    try:
        profile = user.candidate_profile
    except CandidateProfile.DoesNotExist:
        raise serializers.ValidationError("Candidate profile not found. Complete your profile first.")

    return {
        "candidate_full_name": user.full_name,
        "candidate_email": user.email,
        "candidate_phone": profile.phone_number,
        "candidate_location": profile.location,
        "candidate_skills": profile.skills or [],
        "candidate_bio": profile.bio,
        "candidate_resume_url": profile.resume.url if profile.resume else None,
    }


# ============================================================
# JOB APPLICATION — CREATE
# ============================================================

class JobApplicationCreateSerializer(serializers.ModelSerializer):
    job_id = serializers.IntegerField(write_only=True)
    cover_letter = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = JobApplication
        fields = ["job_id", "cover_letter"]

    def validate(self, attrs):
        if self.context["request"].user.role != "candidate":
            raise serializers.ValidationError("Only candidates can apply.")
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        job_id = validated_data["job_id"]

        if JobApplication.objects.filter(job_id=job_id, candidate=user).exists():
            raise serializers.ValidationError("You have already applied to this job.")

        snapshot = build_candidate_snapshot(user)

        return JobApplication.objects.create(
            job_id=job_id,
            candidate=user,
            cover_letter=validated_data.get("cover_letter", ""),
            **snapshot
        )


# ============================================================
# JOB APPLICATION — VIEW
# ============================================================

class JobApplicationSerializer(serializers.ModelSerializer):
    job_id = serializers.IntegerField(source="job.id", read_only=True)
    job_title = serializers.CharField(source="job.title", read_only=True)
    company_name = serializers.CharField(source="job.company_name", read_only=True)

    class Meta:
        model = JobApplication
        fields = [
            "id", "job_id", "job_title", "company_name",
            "candidate_full_name", "candidate_email",
            "candidate_phone", "candidate_location",
            "candidate_skills", "candidate_bio",
            "candidate_resume_url", "cover_letter",
            "status", "created_at", "updated_at",
        ]


# ============================================================
# JOB STATUS UPDATE
# ============================================================

class JobApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = ["status"]

    def update(self, instance, validated_data):
        instance.status = validated_data["status"]
        instance.status_updated_at = timezone.now()
        instance.save()
        return instance


# ============================================================
# INTERNSHIP APPLICATION — CREATE
# ============================================================

class InternshipApplicationCreateSerializer(serializers.ModelSerializer):
    internship_id = serializers.IntegerField(write_only=True)
    cover_letter = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = InternshipApplication
        fields = ["internship_id", "cover_letter"]

    def validate(self, attrs):
        if self.context["request"].user.role != "candidate":
            raise serializers.ValidationError("Only candidates can apply.")
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        internship_id = validated_data["internship_id"]

        if InternshipApplication.objects.filter(internship_id=internship_id, candidate=user).exists():
            raise serializers.ValidationError("You have already applied to this internship.")

        snapshot = build_candidate_snapshot(user)

        return InternshipApplication.objects.create(
            internship_id=internship_id,
            candidate=user,
            cover_letter=validated_data.get("cover_letter", ""),
            **snapshot
        )


# ============================================================
# INTERNSHIP APPLICATION — VIEW
# ============================================================

class InternshipApplicationSerializer(serializers.ModelSerializer):
    internship_title = serializers.CharField(source="internship.title", read_only=True)
    company_name = serializers.CharField(source="internship.company_name", read_only=True)

    class Meta:
        model = InternshipApplication
        fields = [
            "id", "internship_title", "company_name",
            "candidate_full_name", "candidate_email",
            "candidate_phone", "candidate_location",
            "candidate_skills", "candidate_bio",
            "candidate_resume_url", "cover_letter",
            "status", "created_at", "updated_at",
        ]


# ============================================================
# JOB SUMMARY (Used for SavedJobs)
# ============================================================

class JobSummarySerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()
    posted_on = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = ("id", "title", "company_name", "location", "posted_on")

    def get_company_name(self, obj):
        if hasattr(obj, "company") and obj.company and hasattr(obj.company, "company_name"):
            return obj.company.company_name
        if hasattr(obj, "company_name"):
            return obj.company_name
        return "Company"

    def get_posted_on(self, obj):
        return (obj.posted_on or getattr(obj, "created_at", None)).isoformat() if hasattr(obj, "created_at") else None


# ============================================================
# INTERNSHIP SUMMARY (Used for SavedInternships)
# ============================================================

class InternshipSummarySerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()

    class Meta:
        model = Internship
        fields = ("id", "title", "company_name", "location", "posted_on")

    def get_company_name(self, obj):
        return getattr(obj, "company_name", "Company")


# ============================================================
# SAVED JOB SERIALIZER
# ============================================================

class SavedJobSerializer(serializers.ModelSerializer):
    job = JobSummarySerializer(read_only=True)
    job_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Job.objects.all(), source="job"
    )

    class Meta:
        model = SavedJob
        fields = ("id", "job", "job_id", "saved_on")
        read_only_fields = ("id", "saved_on", "job")


# ============================================================
# SAVED INTERNSHIP SERIALIZER
# ============================================================

class SavedInternshipSerializer(serializers.ModelSerializer):
    internship = InternshipSummarySerializer(read_only=True)
    internship_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Internship.objects.all(), source="internship"
    )

    class Meta:
        model = SavedInternship
        fields = ("id", "internship", "internship_id", "saved_on")
        read_only_fields = ("id", "saved_on", "internship")
