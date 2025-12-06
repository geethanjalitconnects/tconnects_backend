from django.conf import settings
from django.db import models
import uuid

class MockInterview(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mock_interviews",
    )
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
        verbose_name = "Mock Interview"
        verbose_name_plural = "Mock Interviews"

    def save(self, *args, **kwargs):
        # generate a pseudo meeting link if none provided
        if not self.meeting_link:
            token = uuid.uuid4().hex[:10]
            self.meeting_link = f"https://meet.example.com/{token}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} — {self.job_role} on {self.scheduled_date} {self.scheduled_time}"
