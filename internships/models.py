# internships/models.py

from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


INTERNSHIP_TYPE_CHOICES = (
    ("full_time", "Full Time"),
    ("part_time", "Part Time"),
    ("remote", "Remote"),
    ("hybrid", "Hybrid"),
)


class Internship(models.Model):
    """
    INTERN MODEL — matches your UI exactly (list page + details page + recruiter posting)
    """

    recruiter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="internships_posted"
    )

    # Main info
    title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    category = models.CharField(max_length=100, blank=True, null=True)  # Risk Management, etc.

    location = models.CharField(max_length=255)

    # Example: "2 Months", "3 Months"
    duration = models.CharField(max_length=50)

    # Example: "₹10,000", "Unpaid", "₹15,000"
    stipend = models.CharField(max_length=100)

    internship_type = models.CharField(
        max_length=50,
        choices=INTERNSHIP_TYPE_CHOICES,
        default="full_time"
    )

    # For list cards
    short_description = models.TextField()

    # Full description for detail page
    full_description = models.TextField()

    # JSON LIST — ["Assist analysts...", "Prepare dashboard"]
    responsibilities = models.JSONField(default=list, blank=True)

    # Skills: ["Excel", "SQL", "Risk Modelling"]
    skills = models.JSONField(default=list, blank=True)

    # Eligibility text
    eligibility = models.TextField(blank=True, null=True)

    # Deadline
    application_deadline = models.DateField(blank=True, null=True)

    # Status
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["location"]),
            models.Index(fields=["category"]),
            models.Index(fields=["internship_type"]),
        ]

    def __str__(self):
        return f"{self.title} – {self.company_name}"
