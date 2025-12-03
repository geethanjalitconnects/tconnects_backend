# applications/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone
from jobs.models import Job
from internships.models import Internship
User = settings.AUTH_USER_MODEL


APPLICATION_STATUS_CHOICES = (
    ("applied", "Applied"),
    ("viewed", "Viewed by Recruiter"),
    ("shortlisted", "Shortlisted"),
    ("rejected", "Rejected"),
    ("withdrawn", "Withdrawn by Candidate"),
)


class JobApplication(models.Model):
    """
    Stores each candidate's application for a Job.
    Keeps a snapshot of candidate profile at apply-time.
    """
    job = models.ForeignKey(
        "jobs.Job",
        on_delete=models.CASCADE,
        related_name="applications"
    )
    candidate = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="job_applications"
    )

    # Snapshot fields (copied from CandidateProfile / FreelancerBasicInfo at apply time)
    candidate_full_name = models.CharField(max_length=255)
    candidate_email = models.EmailField()
    candidate_phone = models.CharField(max_length=50, blank=True, null=True)
    candidate_location = models.CharField(max_length=255, blank=True, null=True)
    candidate_skills = models.JSONField(default=list, blank=True)   # ["Python", "Django"]
    candidate_bio = models.TextField(blank=True, null=True)
    candidate_resume_url = models.CharField(max_length=1024, blank=True, null=True)

    # Application metadata
    cover_letter = models.TextField(blank=True, null=True)  # optional text from candidate
    status = models.CharField(max_length=32, choices=APPLICATION_STATUS_CHOICES, default="applied")
    status_updated_at = models.DateTimeField(blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Optional: recruiter notes (private)
    recruiter_notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ("job", "candidate")  # prevent duplicate applies
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["job"]),
            models.Index(fields=["candidate"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Application: {self.candidate_email} -> {self.job.title}"

    def set_status(self, new_status):
        """Update status and timestamp"""
        if new_status not in dict(APPLICATION_STATUS_CHOICES):
            raise ValueError("Invalid status")
        self.status = new_status
        self.status_updated_at = timezone.now()
        self.save()


class InternshipApplication(models.Model):
    """
    Stores each candidate's application for an Internship.
    """
    internship = models.ForeignKey(
        "internships.Internship",
        on_delete=models.CASCADE,
        related_name="applications"
    )
    candidate = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="internship_applications"
    )

    # Snapshot fields
    candidate_full_name = models.CharField(max_length=255)
    candidate_email = models.EmailField()
    candidate_phone = models.CharField(max_length=50, blank=True, null=True)
    candidate_location = models.CharField(max_length=255, blank=True, null=True)
    candidate_skills = models.JSONField(default=list, blank=True)
    candidate_bio = models.TextField(blank=True, null=True)
    candidate_resume_url = models.CharField(max_length=1024, blank=True, null=True)

    # Application metadata
    cover_letter = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=32, choices=APPLICATION_STATUS_CHOICES, default="applied")
    status_updated_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    recruiter_notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ("internship", "candidate")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["internship"]),
            models.Index(fields=["candidate"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"InternshipApplication: {self.candidate_email} -> {self.internship.title}"

    def set_status(self, new_status):
        """Update status and timestamp"""
        if new_status not in dict(APPLICATION_STATUS_CHOICES):
            raise ValueError("Invalid status")
        self.status = new_status
        self.status_updated_at = timezone.now()
        self.save()
class SavedJob(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_jobs"
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="saved_by"
    )
    saved_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "job")
        ordering = ["-saved_on"]

    def __str__(self):
        return f"{self.user.email} saved {self.job.title}"
class SavedInternship(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_internships"
    )
    internship = models.ForeignKey(
        Internship,
        on_delete=models.CASCADE,
        related_name="saved_by"
    )
    saved_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "internship")
        ordering = ["-saved_on"]

    def __str__(self):
        return f"{self.user.email} saved {self.internship.title}"
