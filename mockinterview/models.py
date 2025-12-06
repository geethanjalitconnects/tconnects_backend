# mockinterview/models.py
from django.conf import settings
from django.db import models
import uuid

class MockInterview(models.Model):
    """Scheduled mock interview"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mock_interviews")
    job_role = models.CharField(max_length=255)
    experience = models.CharField(max_length=100, blank=True)
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    email = models.EmailField()
    interviewer_preference = models.CharField(max_length=255, blank=True)
    special_requests = models.TextField(blank=True)
    meeting_link = models.URLField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-scheduled_date", "-scheduled_time"]

    def save(self, *args, **kwargs):
        # if meeting_link isn't provided, generate a pseudo link
        if not self.meeting_link:
            # using uuid to create unique meeting identifier
            token = uuid.uuid4().hex[:10]
            # dummy meeting link - replace with real meeting provider integration if needed
            self.meeting_link = f"https://meet.example.com/{token}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} - {self.job_role} @ {self.scheduled_date} {self.scheduled_time}"
