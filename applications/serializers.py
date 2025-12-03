# applications/serializers.py

from rest_framework import serializers
from django.utils import timezone

from .models import JobApplication, InternshipApplication
from profiles.models import CandidateProfile
from .models import SavedJob
from jobs.models import Job
from .models import SavedInternship
from internships.models import Internship


# ============================================================
# UTIL — Fetch Candidate Snapshot
# ============================================================

def build_candidate_snapshot(user):
    """
    Fetch full candidate profile snapshot at apply time.
    Used by both job & internship applications.
    """
    try:
        profile = user.candidate_profile  # CandidateProfile
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
        user = self.context["request"].user

        if user.role != "candidate":
            raise serializers.ValidationError("Only candidates can apply.")

        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        job_id = validated_data["job_id"]
        cover_letter = validated_data.get("cover_letter", "")

        # Prevent duplicate apply
        if JobApplication.objects.filter(job_id=job_id, candidate=user).exists():
            raise serializers.ValidationError("You have already applied to this job.")

        # Prepare snapshot
        snapshot = build_candidate_snapshot(user)

        application = JobApplication.objects.create(
            job_id=job_id,
            candidate=user,
            cover_letter=cover_letter,
            **snapshot
        )

        return application


# ============================================================
# JOB APPLICATION — VIEW (DETAIL)
# ============================================================

class JobApplicationSerializer(serializers.ModelSerializer):
    job_id = serializers.IntegerField(source="job.id", read_only=True)
    job_title = serializers.CharField(source="job.title", read_only=True)
    company_name = serializers.CharField(source="job.company_name", read_only=True)

    class Meta:
        model = JobApplication
        fields = [
            "id",
            "job_id",  # ⭐ added for applied status check
            "job_title",
            "company_name",
            "candidate_full_name",
            "candidate_email",
            "candidate_phone",
            "candidate_location",
            "candidate_skills",
            "candidate_bio",
            "candidate_resume_url",
            "cover_letter",
            "status",
            "created_at",
            "updated_at",
        ]



# ============================================================
# JOB APPLICATION — RECRUITER UPDATE STATUS
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
        user = self.context["request"].user

        if user.role != "candidate":
            raise serializers.ValidationError("Only candidates can apply.")

        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        internship_id = validated_data["internship_id"]
        cover_letter = validated_data.get("cover_letter", "")

        # Prevent duplicate apply
        if InternshipApplication.objects.filter(internship_id=internship_id, candidate=user).exists():
            raise serializers.ValidationError("You have already applied to this internship.")

        # Prepare snapshot
        snapshot = build_candidate_snapshot(user)

        application = InternshipApplication.objects.create(
            internship_id=internship_id,
            candidate=user,
            cover_letter=cover_letter,
            **snapshot
        )

        return application


# ============================================================
# INTERNSHIP APPLICATION — VIEW (DETAIL)
# ============================================================

class InternshipApplicationSerializer(serializers.ModelSerializer):
    internship_title = serializers.CharField(source="internship.title", read_only=True)
    company_name = serializers.CharField(source="internship.company_name", read_only=True)

    class Meta:
        model = InternshipApplication
        fields = [
            "id",
            "internship_title",
            "company_name",
            "candidate_full_name",
            "candidate_email",
            "candidate_phone",
            "candidate_location",
            "candidate_skills",
            "candidate_bio",
            "candidate_resume_url",
            "cover_letter",
            "status",
            "created_at",
            "updated_at",
        ]


# ============================================================
# INTERNSHIP APPLICATION — RECRUITER UPDATE STATUS
# ============================================================

class InternshipApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternshipApplication
        fields = ["status"]

    def update(self, instance, validated_data):
        instance.status = validated_data["status"]
        instance.status_updated_at = timezone.now()
        instance.save()
        return instance
# applications/serializers.py
# --------------------------
# Replace the existing JobSummarySerializer with this robust version.

class JobSummarySerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()
    posted_on = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = ("id", "title", "company_name", "location", "posted_on")

    def get_company_name(self, obj):
        """
        Robustly obtain a company name for a Job instance.

        Tries multiple possibilities in order:
        - obj.company.company_name
        - obj.company_name (direct field)
        - obj.recruiter.company_name
        - obj.recruiter.profile.company_name
        - obj.employer.company_name
        - obj.posted_by.company_name
        - obj.company_profile.company_name
        - fallback: "Company"
        """
        try:
            # 1) Job.company -> Company model with company_name
            if hasattr(obj, "company") and getattr(obj, "company"):
                company = getattr(obj, "company")
                if hasattr(company, "company_name"):
                    return company.company_name
                # direct string
                if isinstance(company, str):
                    return company

            # 2) job has direct company_name field
            if hasattr(obj, "company_name") and getattr(obj, "company_name"):
                return getattr(obj, "company_name")

            # 3) recruiter relation (common pattern)
            recruiter = getattr(obj, "recruiter", None)
            if recruiter:
                if hasattr(recruiter, "company_name") and recruiter.company_name:
                    return recruiter.company_name
                # try nested profile
                profile = getattr(recruiter, "profile", None)
                if profile and hasattr(profile, "company_name") and profile.company_name:
                    return profile.company_name

            # 4) other common relation names
            for attr in ("employer", "posted_by", "company_profile"):
                rel = getattr(obj, attr, None)
                if rel:
                    if hasattr(rel, "company_name") and rel.company_name:
                        return rel.company_name
                    if isinstance(rel, str):
                        return rel

        except Exception:
            # swallow and fallback to default to avoid 500s
            pass

        return "Company"

    def get_posted_on(self, obj):
        """
        Return a date (ISO / readable) for when the job was posted.
        Prefer 'posted_on' if present, else fall back to 'created_at'.
        """
        try:
            if hasattr(obj, "posted_on") and getattr(obj, "posted_on"):
                val = getattr(obj, "posted_on")
            else:
                val = getattr(obj, "created_at", None)

            if not val:
                return None

            # return ISO string or date depending on what frontend expects
            # safe approach: return ISO datetime string
            return val.isoformat()
        except Exception:
            return None


    

class SavedJobSerializer(serializers.ModelSerializer):
    job = JobSummarySerializer(read_only=True)
    job_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Job.objects.all(), source="job"
    )

    class Meta:
        model = SavedJob
        fields = ("id", "job", "job_id", "saved_on")
        read_only_fields = ("id", "saved_on", "job")
# ---------------------- Internship Summary ----------------------

class InternshipSummarySerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()

    class Meta:
        model = Internship
        fields = ("id", "title", "company_name", "location", "posted_on")

    def get_company_name(self, obj):
        return getattr(obj, "company_name", "Company")


# ---------------------- Internship Summary ----------------------

class InternshipSummarySerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()

    class Meta:
        model = Internship
        fields = ("id", "title", "company_name", "location", "posted_on")

    def get_company_name(self, obj):
        return getattr(obj, "company_name", "Company")


# ---------------------- Saved Internship ----------------------

class SavedInternshipSerializer(serializers.ModelSerializer):
    internship = InternshipSummarySerializer(read_only=True)
    internship_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=Internship.objects.all(),
        source="internship"
    )

    class Meta:
        model = SavedInternship
        fields = ("id", "internship", "internship_id", "saved_on")
        read_only_fields = ("id", "saved_on", "internship")
