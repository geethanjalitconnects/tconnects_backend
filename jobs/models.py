# jobs/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone

User = settings.AUTH_USER_MODEL


# Employment type list (without internship)
EMPLOYMENT_TYPE_CHOICES = (
    ("full_time", "Full Time"),
    ("part_time", "Part Time"),
    ("contract", "Contract"),
    ("remote", "Remote"),
    ("hybrid", "Hybrid"),
)


class Job(models.Model):
    """
    JOB MODEL — matches your frontend job posting, listing, and details UI perfectly.
    """

    # Recruiter who posted the job
    recruiter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="jobs_posted"
    )

    # MAIN JOB FIELDS
    title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)

    # Example: "1–3 Years"
    experience_range = models.CharField(max_length=100)

    # Example: "6–9 LPA"
    salary_range = models.CharField(max_length=100, blank=True, null=True)

    employment_type = models.CharField(
        max_length=50,
        choices=EMPLOYMENT_TYPE_CHOICES,
        default="full_time"
    )

    category = models.CharField(max_length=100, blank=True, null=True)  
    # Example: Risk Management, AML, Finance, etc.

    short_description = models.TextField()  
    # Used in job list cards

    full_description = models.TextField()
    # Used in JobDetailsPage.jsx

    # JSON LIST → ["Risk Assessment", "Fraud Detection"]
    responsibilities = models.JSONField(default=list, blank=True)

    # JSON LIST → ["Python", "Django", "AML Knowledge"]
    requirements = models.JSONField(default=list, blank=True)

    skills = models.JSONField(default=list, blank=True)
    # Shown as skills badges

    eligible_degrees = models.JSONField(default=list, blank=True)
    # Example: ["B.Tech", "B.Com", "MBA"]

    # Optional deadline
    application_deadline = models.DateField(blank=True, null=True)

    # JOB STATUS
    is_active = models.BooleanField(default=True)

    # TIMESTAMPS
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["location"]),
            models.Index(fields=["employment_type"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self):
        return f"{self.title} – {self.company_name}"
